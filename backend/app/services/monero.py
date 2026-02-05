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
        Check if a payment with given payment_id has been received
        Returns payment details if found
        """
        await self.open_wallet()
        
        result = await self._rpc_call("get_payments", {
            "payment_id": payment_id,
        })
        
        payments = result.get("payments", [])
        if not payments:
            return {
                "received": False,
                "amount": 0,
                "confirmations": 0,
            }
        
        # Get the latest payment
        payment = payments[-1]
        amount = payment.get("amount", 0) / 1e12
        block_height = payment.get("block_height", 0)
        tx_hash = payment.get("tx_hash", "")
        
        # Get current height for confirmations
        height_result = await self._rpc_call("get_height")
        current_height = height_result.get("height", 0)
        confirmations = current_height - block_height if block_height > 0 else 0
        
        return {
            "received": True,
            "amount": amount,
            "confirmations": confirmations,
            "confirmed": confirmations >= self.confirmations_required,
            "tx_hash": tx_hash,
            "block_height": block_height,
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
    
    async def get_exchange_rate(self) -> float:
        """Get current XMR/USD exchange rate"""
        try:
            async with httpx.AsyncClient() as client:
                # Use CoinGecko API (free, no API key needed)
                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={
                        "ids": "monero",
                        "vs_currencies": "usd",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("monero", {}).get("usd", 150.0)  # Default fallback
        except Exception:
            return 150.0  # Fallback rate
    
    async def calculate_xmr_amount(self, usd_amount: float) -> Tuple[float, float]:
        """
        Calculate XMR amount for given USD
        Returns (xmr_amount, exchange_rate)
        """
        rate = await self.get_exchange_rate()
        xmr_amount = usd_amount / rate
        return round(xmr_amount, 12), rate


# Singleton instance
monero_service = MoneroService()
