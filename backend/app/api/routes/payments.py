"""
Payment API routes
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.payment import PaymentRequest, PaymentRequestStatus, PaymentRequestType
from app.models.transaction import Transaction, TransactionType, TransactionStatus, PaymentMethod, Wallet
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionType
from app.models.post import Post
from app.schemas.payment import (
    PaymentRequestCreate,
    PaymentRequestResponse,
    TipCreate,
    UnlockCreate,
    CryptoPaymentInfo,
    PaymentStatusCheck,
)
from app.schemas.transaction import DepositCreate, WalletResponse
from app.schemas.common import SuccessResponse
from app.api.deps import get_current_user
from app.services.monero import monero_service
from app.services.btcpay import btcpay_service

router = APIRouter(prefix="/payments", tags=["Payments"])


def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 PNG"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, "PNG")
    
    return base64.b64encode(buffer.getvalue()).decode()


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's wallet"""
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        wallet = Wallet(user_id=current_user.id)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
    
    return WalletResponse(
        balance=float(wallet.balance),
        pending_balance=float(wallet.pending_balance),
        total_earned=float(wallet.total_earned),
        total_withdrawn=float(wallet.total_withdrawn),
        total_spent=float(wallet.total_spent),
    )


@router.post("/deposit", response_model=PaymentRequestResponse)
async def create_deposit(
    data: DepositCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a deposit request"""
    # Calculate crypto amount
    if data.payment_method == PaymentMethod.MONERO:
        crypto_amount, exchange_rate = await monero_service.calculate_xmr_amount(data.amount)
        integrated_address, payment_id = await monero_service.create_integrated_address()
        
        payment_request = PaymentRequest(
            user_id=current_user.id,
            type=PaymentRequestType.DEPOSIT,
            status=PaymentRequestStatus.AWAITING_PAYMENT,
            amount_usd=data.amount,
            amount_crypto=crypto_amount,
            crypto_currency="XMR",
            exchange_rate=exchange_rate,
            payment_method=PaymentMethod.MONERO,
            monero_address=await monero_service.get_address(),
            monero_payment_id=payment_id,
            monero_integrated_address=integrated_address,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        
    elif data.payment_method == PaymentMethod.BTCPAY:
        # Create BTCPay invoice (anonimlik için e-posta GÖNDERİLMEZ)
        invoice = await btcpay_service.create_invoice(
            amount=data.amount,
            currency="USD",
            order_id=f"deposit_{current_user.id}_{datetime.utcnow().timestamp()}",
            metadata={"user_id": str(current_user.id), "type": "deposit"},
        )
        
        payment_methods = await btcpay_service.get_invoice_payment_methods(invoice["id"])
        btc_method = next((m for m in payment_methods if m.get("cryptoCode") == "BTC"), None)
        
        crypto_amount = float(btc_method.get("due", 0)) if btc_method else 0
        exchange_rate = data.amount / crypto_amount if crypto_amount > 0 else 0
        
        payment_request = PaymentRequest(
            user_id=current_user.id,
            type=PaymentRequestType.DEPOSIT,
            status=PaymentRequestStatus.AWAITING_PAYMENT,
            amount_usd=data.amount,
            amount_crypto=crypto_amount,
            crypto_currency="BTC",
            exchange_rate=exchange_rate,
            payment_method=PaymentMethod.BTCPAY,
            btcpay_invoice_id=invoice["id"],
            btcpay_checkout_url=invoice.get("checkoutLink"),
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz ödeme yöntemi"
        )
    
    db.add(payment_request)
    await db.commit()
    await db.refresh(payment_request)
    
    return PaymentRequestResponse(
        id=payment_request.id,
        type=payment_request.type,
        status=payment_request.status,
        amount_usd=float(payment_request.amount_usd),
        amount_crypto=float(payment_request.amount_crypto) if payment_request.amount_crypto else None,
        crypto_currency=payment_request.crypto_currency,
        exchange_rate=float(payment_request.exchange_rate) if payment_request.exchange_rate else None,
        payment_method=payment_request.payment_method,
        monero_address=payment_request.monero_address,
        monero_payment_id=payment_request.monero_payment_id,
        monero_integrated_address=payment_request.monero_integrated_address,
        btcpay_checkout_url=payment_request.btcpay_checkout_url,
        expires_at=payment_request.expires_at,
        confirmations=payment_request.confirmations,
        created_at=payment_request.created_at,
    )


@router.get("/request/{request_id}/status", response_model=PaymentStatusCheck)
async def check_payment_status(
    request_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check payment request status"""
    result = await db.execute(
        select(PaymentRequest).where(
            and_(
                PaymentRequest.id == request_id,
                PaymentRequest.user_id == current_user.id
            )
        )
    )
    payment_request = result.scalar_one_or_none()
    
    if not payment_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ödeme isteği bulunamadı"
        )
    
    # Check if expired
    if payment_request.expires_at < datetime.utcnow():
        if payment_request.status == PaymentRequestStatus.AWAITING_PAYMENT:
            payment_request.status = PaymentRequestStatus.EXPIRED
            await db.commit()
        
        return PaymentStatusCheck(
            status=PaymentRequestStatus.EXPIRED,
            confirmations=0,
            is_complete=False,
            tx_hash=None,
        )
    
    # Check payment status based on method
    if payment_request.payment_method == PaymentMethod.MONERO:
        payment_info = await monero_service.check_payment(payment_request.monero_payment_id)
        
        if payment_info["received"]:
            payment_request.confirmations = payment_info["confirmations"]
            payment_request.tx_hash = payment_info["tx_hash"]
            
            if payment_info["confirmed"]:
                payment_request.status = PaymentRequestStatus.COMPLETED
                payment_request.confirmed_at = datetime.utcnow()
                
                # Credit wallet
                await _process_completed_payment(payment_request, db)
            else:
                payment_request.status = PaymentRequestStatus.CONFIRMING
            
            await db.commit()
        
    elif payment_request.payment_method == PaymentMethod.BTCPAY:
        invoice_status = await btcpay_service.check_invoice_status(
            payment_request.btcpay_invoice_id
        )
        
        if invoice_status["is_confirmed"]:
            payment_request.status = PaymentRequestStatus.COMPLETED
            payment_request.confirmed_at = datetime.utcnow()
            await _process_completed_payment(payment_request, db)
            await db.commit()
        elif invoice_status["is_paid"]:
            payment_request.status = PaymentRequestStatus.CONFIRMING
            await db.commit()
        elif invoice_status["is_expired"]:
            payment_request.status = PaymentRequestStatus.EXPIRED
            await db.commit()
    
    return PaymentStatusCheck(
        status=payment_request.status,
        confirmations=payment_request.confirmations,
        is_complete=payment_request.status == PaymentRequestStatus.COMPLETED,
        tx_hash=payment_request.tx_hash,
    )


def _request_type_to_tx_type(req_type: PaymentRequestType) -> TransactionType:
    """Ödeme isteği türünü işlem türüne çevirir."""
    mapping = {
        PaymentRequestType.DEPOSIT: TransactionType.DEPOSIT,
        PaymentRequestType.TIP: TransactionType.TIP,
        PaymentRequestType.POST_UNLOCK: TransactionType.POST_UNLOCK,
        PaymentRequestType.MESSAGE_UNLOCK: TransactionType.MESSAGE_UNLOCK,
        PaymentRequestType.SUBSCRIPTION: TransactionType.SUBSCRIPTION,
        PaymentRequestType.STREAM_ACCESS: TransactionType.STREAM_ACCESS,
    }
    return mapping.get(req_type, TransactionType.TIP)


async def _process_completed_payment(
    payment_request: PaymentRequest,
    db: AsyncSession
):
    """
    Tamamlanan bir ödemeyi işler.

    ÖNEMLİ: İdempotent'tir - aynı ödeme isteği birden fazla kez (webhook +
    durum sorgusu) işlenirse bakiye İKİ KEZ yüklenmez. Ayrıca kripto ile
    yapılan bahşiş/PPV ödemelerinde alıcı (içerik üreticisi) artık doğru
    şekilde kredilendirilir (önceki kodda para kayboluyordu).
    """
    # İdempotensi: bu ödeme için zaten bir işlem kaydı varsa tekrar işleme.
    existing_tx = await db.execute(
        select(Transaction).where(Transaction.payment_id == str(payment_request.id))
    )
    if existing_tx.scalar_one_or_none():
        return

    if payment_request.type == PaymentRequestType.DEPOSIT:
        # Kullanıcının cüzdanına bakiye yükle
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == payment_request.user_id)
        )
        wallet = result.scalar_one_or_none()

        if wallet:
            wallet.balance += payment_request.amount_usd

        transaction = Transaction(
            user_id=payment_request.user_id,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=payment_request.amount_usd,
            fee=0,
            net_amount=payment_request.amount_usd,
            payment_method=payment_request.payment_method,
            payment_id=str(payment_request.id),
            crypto_amount=payment_request.amount_crypto,
            crypto_currency=payment_request.crypto_currency,
            exchange_rate=payment_request.exchange_rate,
        )
        db.add(transaction)
        return

    # Bahşiş / PPV / abonelik vb. - alıcıya (içerik üreticisine) öde
    if payment_request.recipient_id:
        amount = float(payment_request.amount_usd)
        platform_fee = amount * (settings.platform_fee_percent / 100)
        net_amount = amount - platform_fee

        # Alıcının cüzdanına net tutarı yükle
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == payment_request.recipient_id)
        )
        recipient_wallet = result.scalar_one_or_none()
        if recipient_wallet:
            recipient_wallet.balance += net_amount
            recipient_wallet.total_earned += net_amount

        post_id = (
            payment_request.reference_id
            if payment_request.reference_type == "post"
            else None
        )
        message = None
        if payment_request.payment_metadata:
            message = payment_request.payment_metadata.get("message")

        transaction = Transaction(
            user_id=payment_request.user_id,
            recipient_id=payment_request.recipient_id,
            type=_request_type_to_tx_type(payment_request.type),
            status=TransactionStatus.COMPLETED,
            amount=amount,
            fee=platform_fee,
            net_amount=net_amount,
            payment_method=payment_request.payment_method,
            payment_id=str(payment_request.id),
            crypto_amount=payment_request.amount_crypto,
            crypto_currency=payment_request.crypto_currency,
            exchange_rate=payment_request.exchange_rate,
            post_id=post_id,
            description=message,
        )
        db.add(transaction)

        # Bahşiş ise gönderinin toplam bahşişini güncelle
        if post_id and payment_request.type == PaymentRequestType.TIP:
            post_result = await db.execute(select(Post).where(Post.id == post_id))
            post = post_result.scalar_one_or_none()
            if post:
                post.tips_total += amount

        # Kripto ile ödenen abonelikte aboneliği aktifleştir
        if payment_request.type == PaymentRequestType.SUBSCRIPTION:
            from datetime import timedelta
            from app.models.subscription import (
                Subscription,
                SubscriptionStatus,
                SubscriptionType,
            )

            months = 1
            if payment_request.payment_metadata:
                try:
                    months = int(payment_request.payment_metadata.get("months", 1) or 1)
                except (TypeError, ValueError):
                    months = 1

            pm = payment_request.payment_method
            subscription = Subscription(
                subscriber_id=payment_request.user_id,
                creator_id=payment_request.recipient_id,
                type=SubscriptionType.PAID,
                status=SubscriptionStatus.ACTIVE,
                amount=amount,
                payment_method=pm.value if hasattr(pm, "value") else str(pm),
                starts_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30 * months),
            )
            db.add(subscription)

            subscriber = await db.get(User, payment_request.user_id)
            creator = await db.get(User, payment_request.recipient_id)
            if creator:
                creator.subscribers_count = (creator.subscribers_count or 0) + 1
            if subscriber:
                subscriber.subscriptions_count = (subscriber.subscriptions_count or 0) + 1


@router.post("/tip", response_model=PaymentRequestResponse)
async def send_tip(
    data: TipCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a tip to a creator"""
    # Get recipient
    result = await db.execute(select(User).where(User.id == data.recipient_id))
    recipient = result.scalar_one_or_none()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendinize bahşiş gönderemezsiniz"
        )
    
    # Check if paying from wallet
    if data.payment_method == "wallet":
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == current_user.id)
        )
        wallet = result.scalar_one_or_none()
        
        if not wallet or wallet.balance < data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yetersiz bakiye"
            )
        
        # Process tip immediately
        platform_fee = data.amount * (settings.platform_fee_percent / 100)
        net_amount = data.amount - platform_fee
        
        # Deduct from sender
        wallet.balance -= data.amount
        wallet.total_spent += data.amount
        
        # Credit recipient
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == recipient.id)
        )
        recipient_wallet = result.scalar_one_or_none()
        
        if recipient_wallet:
            recipient_wallet.balance += net_amount
            recipient_wallet.total_earned += net_amount
        
        # Create transactions
        sender_tx = Transaction(
            user_id=current_user.id,
            recipient_id=recipient.id,
            type=TransactionType.TIP,
            status=TransactionStatus.COMPLETED,
            amount=data.amount,
            fee=platform_fee,
            net_amount=net_amount,
            payment_method=PaymentMethod.WALLET,
            post_id=data.post_id,
            description=data.message,
        )
        db.add(sender_tx)
        
        # Update post tip total if applicable
        if data.post_id:
            result = await db.execute(select(Post).where(Post.id == data.post_id))
            post = result.scalar_one_or_none()
            if post:
                post.tips_total += data.amount
        
        await db.commit()
        
        # Return mock payment request for consistency
        return PaymentRequestResponse(
            id=sender_tx.id,
            type=PaymentRequestType.TIP,
            status=PaymentRequestStatus.COMPLETED,
            amount_usd=data.amount,
            amount_crypto=None,
            crypto_currency="",
            exchange_rate=None,
            payment_method=PaymentMethod.WALLET,
            monero_address=None,
            monero_payment_id=None,
            monero_integrated_address=None,
            btcpay_checkout_url=None,
            expires_at=datetime.utcnow(),
            confirmations=0,
            created_at=datetime.utcnow(),
        )
    
    # Create crypto payment request
    if data.payment_method == "monero":
        crypto_amount, exchange_rate = await monero_service.calculate_xmr_amount(data.amount)
        integrated_address, payment_id = await monero_service.create_integrated_address()
        
        payment_request = PaymentRequest(
            user_id=current_user.id,
            type=PaymentRequestType.TIP,
            status=PaymentRequestStatus.AWAITING_PAYMENT,
            amount_usd=data.amount,
            amount_crypto=crypto_amount,
            crypto_currency="XMR",
            exchange_rate=exchange_rate,
            payment_method=PaymentMethod.MONERO,
            monero_address=await monero_service.get_address(),
            monero_payment_id=payment_id,
            monero_integrated_address=integrated_address,
            recipient_id=recipient.id,
            reference_type="post" if data.post_id else None,
            reference_id=data.post_id,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            payment_metadata={"message": data.message} if data.message else None,
        )
        
    elif data.payment_method == "btcpay":
        invoice = await btcpay_service.create_invoice(
            amount=data.amount,
            currency="USD",
            order_id=f"tip_{current_user.id}_{recipient.id}_{datetime.utcnow().timestamp()}",
            metadata={
                "user_id": str(current_user.id),
                "recipient_id": str(recipient.id),
                "type": "tip",
                "message": data.message,
            },
        )
        
        crypto_amount, exchange_rate = await btcpay_service.calculate_btc_amount(data.amount)
        
        payment_request = PaymentRequest(
            user_id=current_user.id,
            type=PaymentRequestType.TIP,
            status=PaymentRequestStatus.AWAITING_PAYMENT,
            amount_usd=data.amount,
            amount_crypto=crypto_amount,
            crypto_currency="BTC",
            exchange_rate=exchange_rate,
            payment_method=PaymentMethod.BTCPAY,
            btcpay_invoice_id=invoice["id"],
            btcpay_checkout_url=invoice.get("checkoutLink"),
            recipient_id=recipient.id,
            reference_type="post" if data.post_id else None,
            reference_id=data.post_id,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            payment_metadata={"message": data.message} if data.message else None,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz ödeme yöntemi"
        )
    
    db.add(payment_request)
    await db.commit()
    await db.refresh(payment_request)
    
    return PaymentRequestResponse(
        id=payment_request.id,
        type=payment_request.type,
        status=payment_request.status,
        amount_usd=float(payment_request.amount_usd),
        amount_crypto=float(payment_request.amount_crypto) if payment_request.amount_crypto else None,
        crypto_currency=payment_request.crypto_currency,
        exchange_rate=float(payment_request.exchange_rate) if payment_request.exchange_rate else None,
        payment_method=payment_request.payment_method,
        monero_address=payment_request.monero_address,
        monero_payment_id=payment_request.monero_payment_id,
        monero_integrated_address=payment_request.monero_integrated_address,
        btcpay_checkout_url=payment_request.btcpay_checkout_url,
        expires_at=payment_request.expires_at,
        confirmations=payment_request.confirmations,
        created_at=payment_request.created_at,
    )


@router.post("/posts/{post_id}/unlock", response_model=PaymentRequestResponse)
async def unlock_post(
    post_id: UUID,
    data: UnlockCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlock a PPV post"""
    # Get post
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post bulunamadı"
        )
    
    if not post.is_ppv or not post.ppv_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu post ücretli değil"
        )
    
    # Check if already unlocked
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.post_id == post_id,
                Transaction.type == TransactionType.POST_UNLOCK,
                Transaction.status == TransactionStatus.COMPLETED
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu içerik zaten açılmış"
        )
    
    amount = float(post.ppv_price)
    
    # Check if paying from wallet
    if data.payment_method == "wallet":
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == current_user.id)
        )
        wallet = result.scalar_one_or_none()
        
        if not wallet or wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yetersiz bakiye"
            )
        
        # Process unlock immediately
        platform_fee = amount * (settings.platform_fee_percent / 100)
        net_amount = amount - platform_fee
        
        wallet.balance -= amount
        wallet.total_spent += amount
        
        # Credit creator
        result = await db.execute(
            select(Wallet).where(Wallet.user_id == post.author_id)
        )
        creator_wallet = result.scalar_one_or_none()
        if creator_wallet:
            creator_wallet.balance += net_amount
            creator_wallet.total_earned += net_amount
        
        # Create transaction
        transaction = Transaction(
            user_id=current_user.id,
            recipient_id=post.author_id,
            type=TransactionType.POST_UNLOCK,
            status=TransactionStatus.COMPLETED,
            amount=amount,
            fee=platform_fee,
            net_amount=net_amount,
            payment_method=PaymentMethod.WALLET,
            post_id=post_id,
        )
        db.add(transaction)
        await db.commit()
        
        return PaymentRequestResponse(
            id=transaction.id,
            type=PaymentRequestType.POST_UNLOCK,
            status=PaymentRequestStatus.COMPLETED,
            amount_usd=amount,
            amount_crypto=None,
            crypto_currency="",
            exchange_rate=None,
            payment_method=PaymentMethod.WALLET,
            monero_address=None,
            monero_payment_id=None,
            monero_integrated_address=None,
            btcpay_checkout_url=None,
            expires_at=datetime.utcnow(),
            confirmations=0,
            created_at=datetime.utcnow(),
        )
    
    # Create crypto payment request (similar to tip)
    # ... (abbreviated for brevity, similar pattern to tip)
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Şu an sadece cüzdan ödemesi destekleniyor"
    )


# Webhook endpoints
@router.post("/webhooks/btcpay")
async def btcpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle BTCPay Server webhooks"""
    body = await request.body()
    signature = request.headers.get("BTCPay-Sig", "")
    
    if not btcpay_service.verify_webhook_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    data = await request.json()
    event_type = data.get("type")
    invoice_id = data.get("invoiceId")
    
    if not invoice_id:
        return {"status": "ok"}
    
    # Find payment request
    result = await db.execute(
        select(PaymentRequest).where(PaymentRequest.btcpay_invoice_id == invoice_id)
    )
    payment_request = result.scalar_one_or_none()
    
    if not payment_request:
        return {"status": "ok"}
    
    if event_type == "InvoiceSettled":
        payment_request.status = PaymentRequestStatus.COMPLETED
        payment_request.confirmed_at = datetime.utcnow()
        await _process_completed_payment(payment_request, db)
    elif event_type == "InvoicePaymentSettled":
        payment_request.status = PaymentRequestStatus.CONFIRMING
    elif event_type == "InvoiceExpired":
        payment_request.status = PaymentRequestStatus.EXPIRED
    
    await db.commit()
    
    return {"status": "ok"}


@router.post("/webhooks/monero")
async def monero_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Monero payment notifications (called by background worker)"""
    data = await request.json()
    payment_id = data.get("payment_id")
    
    if not payment_id:
        return {"status": "ok"}
    
    result = await db.execute(
        select(PaymentRequest).where(PaymentRequest.monero_payment_id == payment_id)
    )
    payment_request = result.scalar_one_or_none()
    
    if not payment_request:
        return {"status": "ok"}
    
    # Check payment
    payment_info = await monero_service.check_payment(payment_id)
    
    if payment_info["confirmed"]:
        payment_request.status = PaymentRequestStatus.COMPLETED
        payment_request.confirmed_at = datetime.utcnow()
        payment_request.tx_hash = payment_info["tx_hash"]
        payment_request.confirmations = payment_info["confirmations"]
        await _process_completed_payment(payment_request, db)
    elif payment_info["received"]:
        payment_request.status = PaymentRequestStatus.CONFIRMING
        payment_request.tx_hash = payment_info["tx_hash"]
        payment_request.confirmations = payment_info["confirmations"]
    
    await db.commit()
    
    return {"status": "ok"}
