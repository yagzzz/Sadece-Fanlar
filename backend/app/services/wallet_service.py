"""
Merkezi cüzdan servisi — tüm para hareketleri buradan geçer.

Bakiyeler TL (TRY) cinsindendir. Komisyon (platform payı) transfer anında
kesilir: alıcı net tutarı alır, fark platformda kalır (Transaction.fee).
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import (
    Wallet,
    Transaction,
    TransactionType,
    TransactionStatus,
    PaymentMethod,
)


async def get_or_create_wallet(db: AsyncSession, user_id: UUID) -> Wallet:
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=user_id)
        db.add(wallet)
        await db.flush()
    return wallet


async def credit(
    db: AsyncSession,
    user_id: UUID,
    amount: float,
    tx_type: TransactionType,
    description: str = "",
    payment_method: PaymentMethod = PaymentMethod.WALLET,
    payment_id: Optional[str] = None,
    commit: bool = True,
) -> Transaction:
    """Kullanıcının bakiyesine para ekler (deposit, manuel kredi vb.)."""
    amount = round(float(amount), 2)
    wallet = await get_or_create_wallet(db, user_id)
    wallet.balance = float(wallet.balance) + amount

    tx = Transaction(
        user_id=user_id,
        recipient_id=user_id,
        type=tx_type,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        fee=0,
        net_amount=amount,
        currency="TRY",
        payment_method=payment_method,
        payment_id=payment_id,
        description=description,
    )
    db.add(tx)
    if commit:
        await db.commit()
        await db.refresh(tx)
    return tx


async def transfer(
    db: AsyncSession,
    from_user_id: UUID,
    to_user_id: UUID,
    amount: float,
    tx_type: TransactionType,
    fee_percent: float,
    description: str = "",
    subscription_id: Optional[UUID] = None,
    post_id: Optional[UUID] = None,
    message_id: Optional[UUID] = None,
    commit: bool = True,
) -> Transaction:
    """
    Bakiyeden bakiyeye komisyonlu transfer.
    Gönderenden `amount` düşülür, alıcıya `net` (komisyon düşülmüş) eklenir.
    Komisyon platformda kalır.
    """
    amount = round(float(amount), 2)
    fee = round(amount * (float(fee_percent) / 100.0), 2)
    net = round(amount - fee, 2)

    from_wallet = await get_or_create_wallet(db, from_user_id)
    if float(from_wallet.balance) < amount:
        raise ValueError("Yetersiz bakiye")

    to_wallet = await get_or_create_wallet(db, to_user_id)

    from_wallet.balance = float(from_wallet.balance) - amount
    from_wallet.total_spent = float(from_wallet.total_spent) + amount

    to_wallet.balance = float(to_wallet.balance) + net
    to_wallet.total_earned = float(to_wallet.total_earned) + net

    tx = Transaction(
        user_id=from_user_id,
        recipient_id=to_user_id,
        type=tx_type,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        fee=fee,
        net_amount=net,
        currency="TRY",
        payment_method=PaymentMethod.WALLET,
        description=description,
        subscription_id=subscription_id,
        post_id=post_id,
        message_id=message_id,
    )
    db.add(tx)
    if commit:
        await db.commit()
        await db.refresh(tx)
    return tx


async def hold(db: AsyncSession, user_id: UUID, amount: float) -> Wallet:
    """Escrow için: bakiyeden düşüp pending_balance'a (emanet) alır."""
    amount = round(float(amount), 2)
    wallet = await get_or_create_wallet(db, user_id)
    if float(wallet.balance) < amount:
        raise ValueError("Yetersiz bakiye")
    wallet.balance = float(wallet.balance) - amount
    wallet.pending_balance = float(wallet.pending_balance) + amount
    return wallet


async def release_hold(
    db: AsyncSession,
    from_user_id: UUID,
    to_user_id: UUID,
    amount: float,
    fee_percent: float,
    tx_type: TransactionType,
    description: str = "",
    commit: bool = True,
) -> Transaction:
    """Escrow serbest bırak: emanetteki tutarı alıcıya (komisyonlu) aktarır."""
    amount = round(float(amount), 2)
    fee = round(amount * (float(fee_percent) / 100.0), 2)
    net = round(amount - fee, 2)

    from_wallet = await get_or_create_wallet(db, from_user_id)
    from_wallet.pending_balance = max(0.0, float(from_wallet.pending_balance) - amount)
    from_wallet.total_spent = float(from_wallet.total_spent) + amount

    to_wallet = await get_or_create_wallet(db, to_user_id)
    to_wallet.balance = float(to_wallet.balance) + net
    to_wallet.total_earned = float(to_wallet.total_earned) + net

    tx = Transaction(
        user_id=from_user_id,
        recipient_id=to_user_id,
        type=tx_type,
        status=TransactionStatus.COMPLETED,
        amount=amount,
        fee=fee,
        net_amount=net,
        currency="TRY",
        payment_method=PaymentMethod.WALLET,
        description=description,
    )
    db.add(tx)
    if commit:
        await db.commit()
        await db.refresh(tx)
    return tx


async def refund_hold(db: AsyncSession, user_id: UUID, amount: float, commit: bool = True) -> Wallet:
    """Escrow iadesi: emanetteki tutarı kullanılabilir bakiyeye geri verir."""
    amount = round(float(amount), 2)
    wallet = await get_or_create_wallet(db, user_id)
    wallet.pending_balance = max(0.0, float(wallet.pending_balance) - amount)
    wallet.balance = float(wallet.balance) + amount
    if commit:
        await db.commit()
    return wallet
