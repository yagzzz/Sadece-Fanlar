"""
BTCPay Server payment service
"""
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from uuid import UUID
import httpx

from app.core.config import settings


class BTCPayService:
    """Service for Bitcoin/Lightning payments via BTCPay Server"""
    
    def __init__(self):
        self.base_url = settings.btcpay_url
        self.api_key = settings.btcpay_api_key
        self.store_id = settings.btcpay_store_id
        self.webhook_secret = settings.btcpay_webhook_secret
    
    def _headers(self) -> dict:
        """Get API headers"""
        return {
            "Authorization": f"token {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def create_invoice(
        self,
        amount: float,
        currency: str = "USD",
        order_id: Optional[str] = None,
        buyer_email: Optional[str] = None,
        redirect_url: Optional[str] = None,
        metadata: Optional[dict] = None,
        expiration_minutes: int = 60,
    ) -> dict:
        """
        Create a payment invoice
        Returns invoice details including checkout URL
        """
        payload = {
            "amount": amount,
            "currency": currency,
            "checkout": {
                "speedPolicy": "MediumSpeed",  # 1 confirmation
                "expirationMinutes": expiration_minutes,
                "monitoringMinutes": 60 * 24,  # Monitor for 24 hours
                "paymentTolerance": 0,
                "redirectURL": redirect_url,
                "redirectAutomatically": True if redirect_url else False,
            },
        }
        
        if order_id:
            payload["orderId"] = order_id
        
        if buyer_email:
            payload["buyer"] = {"email": buyer_email}
        
        if metadata:
            payload["metadata"] = metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/stores/{self.store_id}/invoices",
                headers=self._headers(),
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_invoice(self, invoice_id: str) -> dict:
        """Get invoice details"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/stores/{self.store_id}/invoices/{invoice_id}",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_invoice_payment_methods(self, invoice_id: str) -> list:
        """Get available payment methods for invoice"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/stores/{self.store_id}/invoices/{invoice_id}/payment-methods",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def check_invoice_status(self, invoice_id: str) -> dict:
        """
        Check invoice payment status
        Returns status details
        """
        invoice = await self.get_invoice(invoice_id)
        
        status = invoice.get("status", "New")
        additional_status = invoice.get("additionalStatus", "None")
        
        return {
            "status": status,
            "additional_status": additional_status,
            "is_paid": status in ["Settled", "Processing"],
            "is_confirmed": status == "Settled",
            "is_expired": status == "Expired",
            "is_invalid": status == "Invalid",
            "amount": invoice.get("amount"),
            "currency": invoice.get("currency"),
            "checkout_link": invoice.get("checkoutLink"),
        }
    
    async def create_payout(
        self,
        destination: str,
        amount: float,
        payment_method: str = "BTC",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a payout (withdrawal) to external address
        """
        payload = {
            "destination": destination,
            "amount": str(amount),
            "paymentMethod": payment_method,
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/stores/{self.store_id}/payouts",
                headers=self._headers(),
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_payout(self, payout_id: str) -> dict:
        """Get payout details"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/stores/{self.store_id}/payouts/{payout_id}",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_exchange_rate(self, crypto: str = "BTC") -> float:
        """Get current exchange rate"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/stores/{self.store_id}/rates",
                    headers=self._headers(),
                    params={"currencyPair": f"{crypto}_USD"},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                for rate in data:
                    if rate.get("currencyPair") == f"{crypto}_USD":
                        return float(rate.get("rate", 0))
                
                return 0
        except Exception:
            return 0
    
    async def calculate_btc_amount(self, usd_amount: float) -> Tuple[float, float]:
        """
        Calculate BTC amount for given USD
        Returns (btc_amount, exchange_rate)
        """
        rate = await self.get_exchange_rate("BTC")
        if rate == 0:
            # Fallback to CoinGecko
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.coingecko.com/api/v3/simple/price",
                        params={"ids": "bitcoin", "vs_currencies": "usd"},
                        timeout=10.0,
                    )
                    data = response.json()
                    rate = data.get("bitcoin", {}).get("usd", 50000)
            except Exception:
                rate = 50000  # Fallback
        
        btc_amount = usd_amount / rate
        return round(btc_amount, 8), rate
    
    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        """Verify BTCPay webhook signature"""
        if not self.webhook_secret:
            return True  # Skip verification if no secret configured
        
        expected = hmac.new(
            self.webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected}", signature)
    
    async def get_supported_payment_methods(self) -> list:
        """Get list of supported payment methods for the store"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/stores/{self.store_id}/payment-methods",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_wallet_balance(self) -> dict:
        """Get store wallet balance"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/stores/{self.store_id}/payment-methods/onchain/BTC/wallet",
                headers=self._headers(),
                timeout=30.0,
            )
            if response.status_code == 404:
                return {"balance": 0, "unconfirmedBalance": 0}
            response.raise_for_status()
            return response.json()


# Singleton instance
btcpay_service = BTCPayService()
