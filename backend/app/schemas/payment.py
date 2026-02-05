"""
Ödeme Şemaları (Schemas)
========================
Bu dosya ödeme işlemleri ile ilgili Pydantic şemalarını içerir.
Monero ve BTCPay ile kripto para ödemeleri desteklenir.

Şemalar:
- PaymentRequestCreate: Ödeme isteği oluşturma
- PaymentRequestResponse: Ödeme isteği yanıtı
- TipCreate: Bahşiş gönderme
- UnlockCreate: İçerik kilidi açma
- CryptoPaymentInfo: Kripto ödeme bilgileri
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.payment import PaymentRequestStatus, PaymentRequestType
from app.models.transaction import PaymentMethod


class PaymentRequestCreate(BaseModel):
    """
    Ödeme İsteği Oluşturma Şeması
    -----------------------------
    Yeni ödeme başlatmak için gerekli bilgiler.
    """
    type: PaymentRequestType = Field(..., description="Ödeme türü")
    amount: float = Field(..., ge=1, description="Tutar (USD)")
    payment_method: PaymentMethod = Field(..., description="Ödeme yöntemi (monero/btcpay)")
    
    # Bahşiş, abonelik vb. için ek bilgiler
    recipient_id: Optional[UUID] = Field(None, description="Alıcı kullanıcı ID'si")
    reference_type: Optional[str] = Field(None, description="Referans türü (post, message, vb.)")
    reference_id: Optional[UUID] = Field(None, description="Referans öğe ID'si")


class PaymentRequestResponse(BaseModel):
    """
    Ödeme İsteği Yanıtı
    -------------------
    Oluşturulan ödeme isteğinin tüm bilgileri.
    Kullanıcıya ödeme adresi ve detayları gösterilir.
    """
    id: UUID
    
    type: PaymentRequestType      # Ödeme türü
    status: PaymentRequestStatus  # Mevcut durum
    
    # Tutar bilgileri
    amount_usd: float             # USD cinsinden tutar
    amount_crypto: Optional[float]  # Kripto cinsinden tutar
    crypto_currency: str          # Kripto para birimi (XMR, BTC)
    exchange_rate: Optional[float]  # Dönüşüm kuru
    
    payment_method: PaymentMethod
    
    # Monero için özel alanlar
    monero_address: Optional[str]          # Ana cüzdan adresi
    monero_payment_id: Optional[str]       # Payment ID
    monero_integrated_address: Optional[str]  # Entegre adres (adres+payment_id)
    
    # BTCPay için özel alanlar
    btcpay_checkout_url: Optional[str]     # Ödeme sayfası URL'i
    
    expires_at: datetime           # Son geçerlilik tarihi
    confirmations: int             # Blockchain onay sayısı
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class TipCreate(BaseModel):
    """
    Bahşiş Gönderme Şeması
    ----------------------
    İçerik üreticisine bahşiş göndermek için.
    İsteğe bağlı mesaj eklenebilir.
    """
    recipient_id: UUID = Field(..., description="Alıcı kullanıcı ID'si")
    amount: float = Field(..., ge=1, le=500, description="Bahşiş miktarı (1-500 USD)")
    payment_method: str = Field(..., pattern="^(monero|btcpay|wallet)$", description="Ödeme yöntemi")
    message: Optional[str] = Field(None, max_length=200, description="Bahşiş ile gönderilecek mesaj")
    
    # İsteğe bağlı: belirli bir gönderiye bahşiş
    post_id: Optional[UUID] = Field(None, description="Gönderi ID'si (isteğe bağlı)")


class UnlockCreate(BaseModel):
    """
    İçerik Kilidi Açma Şeması
    -------------------------
    PPV içeriğin kilidini açmak için.
    """
    payment_method: str = Field(..., pattern="^(monero|btcpay|wallet)$", description="Ödeme yöntemi")


class CryptoPaymentInfo(BaseModel):
    """
    Kripto Ödeme Bilgileri
    ----------------------
    Kullanıcıya gösterilecek ödeme detayları.
    QR kod ile kolay ödeme desteklenir.
    """
    currency: str           # Para birimi (XMR, BTC)
    amount: float           # Ödenecek miktar
    address: str            # Cüzdan adresi
    payment_id: Optional[str] = None  # Monero payment ID
    qr_code: str            # Base64 kodlanmış QR kod
    expires_at: datetime    # Son ödeme tarihi
    exchange_rate: float    # Dönüşüm kuru (1 kripto = ? USD)
    
    # BTCPay için
    checkout_url: Optional[str] = None  # Ödeme sayfası URL'i


class PaymentStatusCheck(BaseModel):
    """
    Ödeme Durumu Kontrolü
    ---------------------
    Ödemenin mevcut durumunu kontrol etmek için.
    """
    status: PaymentRequestStatus  # Mevcut durum
    confirmations: int            # Blockchain onay sayısı
    is_complete: bool             # Tamamlandı mı?
    tx_hash: Optional[str]        # İşlem hash'i (tamamlandıysa)
