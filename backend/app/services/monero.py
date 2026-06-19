"""
Monero payment service
"""
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
import httpx

from app.core.config import settings


class MoneroService:
    """Service for Monero payments via monero-wallet-rpc"""
    
    def __init__(self):
        self.rpc_url = settings.monero_wallet_rpc_url
        self.rpc_user = settings.monero_wallet_rpc_user
        self.rpc_password = settings.monero_wallet_rpc_password
        self.wallet_name = settings.monero_wallet_name
        self.confirmations_required = settings.monero_confirmations_required
    
    async def _rpc_call(self, method: str, params: Optional[dict] = None) -> dict:
        """Make an RPC call to monero-wallet-rpc"""
        payload = {
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": params or {},
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.rpc_url}/json_rpc",
                json=payload,
                auth=(self.rpc_user, self.rpc_password),
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"Monero RPC error: {result['error']}")
            
            return result.get("result", {})
    
    async def open_wallet(self) -> bool:
        """Open the wallet"""
        try:
            await self._rpc_call("open_wallet", {
                "filename": self.wallet_name,
            })
            return True
        except Exception:
            # Wallet might already be open
            return True
    
    async def create_wallet(self) -> bool:
        """Create a new wallet if it doesn't exist"""
        try:
            await self._rpc_call("create_wallet", {
                "filename": self.wallet_name,
                "language": "English",
            })
            return True
        except Exception:
            return False
    
    async def get_balance(self) -> Tuple[float, float]:
        """Get wallet balance (total, unlocked)"""
        await self.open_wallet()
        result = await self._rpc_call("get_balance")
        
        # Convert from atomic units (1 XMR = 10^12 atomic units)
        balance = result.get("balance", 0) / 1e12
        unlocked = result.get("unlocked_balance", 0) / 1e12
        
        return balance, unlocked
    
    async def get_address(self) -> str:
        """Get the primary wallet address"""
        await self.open_wallet()
        result = await self._rpc_call("get_address")
        return result.get("address", "")
    
    async def create_integrated_address(self, payment_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Create an integrated address for receiving payment
        Returns (integrated_address, payment_id)
        """
        await self.open_wallet()
        
        # Generate payment ID if not provided (16 hex chars)
        if not payment_id:
            payment_id = secrets.token_hex(8)
        
        result = await self._rpc_call("make_integrated_address", {
            "payment_id": payment_id,
        })
        
        return result.get("integrated_address", ""), payment_id
    
    async def create_subaddress(self, label: str = "") -> Tuple[str, int]:
        """
        Create a new subaddress for receiving payment
        Returns (address, index)
        """
        await self.open_wallet()
        
        result = await self._rpc_call("create_address", {
            "account_index": 0,
            "label": label,
        })
        
        return result.get("address", ""), result.get("address_index", 0)
    
    async def check_payment(self, payment_id: str) -> dict:
        """
        Verilen payment_id için gelen TÜM ödemeleri toplar.

        Tek bir payment_id'ye birden fazla transfer gelebilir; hepsini toplayıp
        toplam alınan XMR'yi döndürür. Onay sayısı, en yeni (en az onaylı) ödemeye
        göre hesaplanır (muhafazakar): hepsi yeterince onaylanmadan "confirmed"
        sayılmaz. Bu, eksik/parçalı ödeme istismarını ve erken kredilemeyi önler.
        """
        await self.open_wallet()
        
        result = await self._rpc_call("get_payments", {
            "payment_id": payment_id,
        })
        
        payments = result.get("payments", [])
        if not payments:
            return {
                "received": False,
                "amount": 0.0,
                "confirmations": 0,
                "confirmed": False,
                "tx_hash": "",
            }
        
        # Tüm ödemeleri topla (atomic units -> XMR)
        total_atomic = sum(int(p.get("amount", 0)) for p in payments)
        total_amount = total_atomic / 1e12
        tx_hashes = [p.get("tx_hash", "") for p in payments if p.get("tx_hash")]
        
        # Onay sayısı: en yeni ödemeye göre (en yüksek block_height = en az onay)
        height_result = await self._rpc_call("get_height")
        current_height = height_result.get("height", 0)
        block_heights = [int(p.get("block_height", 0)) for p in payments if int(p.get("block_height", 0)) > 0]
        if block_heights:
            newest_block = max(block_heights)
            confirmations = max(0, current_height - newest_block)
        else:
            # Henüz bloğa girmemiş (mempool)
            confirmations = 0
        
        return {
            "received": True,
            "amount": round(total_amount, 12),
            "confirmations": confirmations,
            "confirmed": confirmations >= self.confirmations_required,
            "tx_hash": tx_hashes[-1] if tx_hashes else "",
            "tx_hashes": tx_hashes,
        }
    
    async def check_incoming_transfers(self, subaddress_index: Optional[int] = None) -> list:
        """Check incoming transfers to wallet or specific subaddress"""
        await self.open_wallet()
        
        params = {
            "transfer_type": "all",
            "account_index": 0,
        }
        
        if subaddress_index is not None:
            params["subaddr_indices"] = [subaddress_index]
        
        result = await self._rpc_call("incoming_transfers", params)
        
        transfers = []
        for t in result.get("transfers", []):
            transfers.append({
                "amount": t.get("amount", 0) / 1e12,
                "tx_hash": t.get("tx_hash", ""),
                "subaddr_index": t.get("subaddr_index", 0),
                "spent": t.get("spent", False),
            })
        
        return transfers
    
    async def send_payment(
        self,
        address: str,
        amount: float,
        priority: int = 1
    ) -> Tuple[str, float]:
        """
        Send XMR to an address
        Returns (tx_hash, fee)
        """
        await self.open_wallet()
        
        # Convert to atomic units
        amount_atomic = int(amount * 1e12)
        
        result = await self._rpc_call("transfer", {
            "destinations": [{
                "amount": amount_atomic,
                "address": address,
            }],
            "priority": priority,
            "get_tx_key": True,
        })
        
        tx_hash = result.get("tx_hash", "")
        fee = result.get("fee", 0) / 1e12
        
        return tx_hash, fee
    
    async def get_exchange_rate(self, vs_currency: str = "try") -> float:
        """
        XMR fiyatını verilen para biriminde döndürür (varsayılan: TRY).
        Platform bakiyeleri TL tutulduğundan varsayılan 'try'.
        """
        fallback = {"try": 5000.0, "usd": 150.0}.get(vs_currency, 150.0)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": "monero", "vs_currencies": vs_currency},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("monero", {}).get(vs_currency, fallback)
        except Exception:
            return fallback

    async def calculate_xmr_amount(self, fiat_amount: float, vs_currency: str = "try") -> Tuple[float, float]:
        """
        Verilen fiat tutar (varsayılan TL) için XMR miktarını hesaplar.
        Returns (xmr_amount, exchange_rate)
        """
        rate = await self.get_exchange_rate(vs_currency)
        xmr_amount = fiat_amount / rate if rate else 0
        return round(xmr_amount, 12), rate


# Singleton instance
monero_service = MoneroService()
