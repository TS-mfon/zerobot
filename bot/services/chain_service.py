"""Thin async wrapper around web3.py for the 0G EVM chain (mainnet)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from eth_account import Account
from web3 import Web3

from bot.config import settings

logger = logging.getLogger(__name__)

# Module-level Web3 instance
w3 = Web3(Web3.HTTPProvider(settings.og_rpc_url, request_kwargs={"timeout": 30}))

# Expose the chain ID so other modules can use it for signing
CHAIN_ID: int = settings.og_chain_id


def is_connected() -> bool:
    """Return True when the RPC node is reachable."""
    try:
        return w3.is_connected()
    except Exception:
        return False


def get_balance(address: str) -> int:
    """Return the native token balance in wei for *address*."""
    checksum = Web3.to_checksum_address(address)
    return w3.eth.get_balance(checksum)


def get_block_number() -> int:
    """Return the latest block number."""
    return w3.eth.block_number


def get_transaction(tx_hash: str) -> Optional[Dict[str, Any]]:
    """Fetch a transaction by hash.  Returns None when not found."""
    try:
        tx = w3.eth.get_transaction(tx_hash)
        return dict(tx)
    except Exception:
        return None


def get_transaction_receipt(tx_hash: str) -> Optional[Dict[str, Any]]:
    """Fetch the receipt for a mined transaction."""
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        return dict(receipt)
    except Exception:
        return None


def get_block(block_identifier: Any) -> Optional[Dict[str, Any]]:
    """Return block data for *block_identifier* (number or 'latest')."""
    try:
        block = w3.eth.get_block(block_identifier)
        return dict(block)
    except Exception:
        return None


def get_gas_price() -> int:
    """Return the current gas price in wei."""
    return w3.eth.gas_price


def send_raw_transaction(signed_tx: bytes) -> str:
    """Broadcast a signed transaction and return the tx hash hex."""
    tx_hash = w3.eth.send_raw_transaction(signed_tx)
    return tx_hash.hex()


def estimate_gas(tx_params: Dict[str, Any]) -> int:
    """Estimate gas for a transaction dict."""
    return w3.eth.estimate_gas(tx_params)


def get_nonce(address: str) -> int:
    """Return the current transaction count (nonce) for *address*."""
    checksum = Web3.to_checksum_address(address)
    return w3.eth.get_transaction_count(checksum)


async def send_native(
    private_key: str,
    from_address: str,
    to_address: str,
    amount_og: float,
    gas: int = 21_000,
) -> str:
    """Send a native OG value transfer. Returns tx hash hex."""

    def _build_sign():
        from_checksum = Web3.to_checksum_address(from_address)
        to_checksum = Web3.to_checksum_address(to_address)
        nonce = w3.eth.get_transaction_count(from_checksum)
        gas_price = int(w3.eth.gas_price * 1.1)
        tx = {
            "from": from_checksum,
            "to": to_checksum,
            "value": Web3.to_wei(amount_og, "ether"),
            "nonce": nonce,
            "gas": gas,
            "gasPrice": gas_price,
            "chainId": CHAIN_ID,
        }
        signed = Account.sign_transaction(tx, private_key)
        return signed.raw_transaction

    raw = await asyncio.to_thread(_build_sign)
    tx_hash = await asyncio.to_thread(w3.eth.send_raw_transaction, raw)
    h = tx_hash.hex()
    return h if h.startswith("0x") else "0x" + h


async def wait_for_receipt(tx_hash: str, attempts: int = 30, interval: float = 2.0) -> Optional[Dict[str, Any]]:
    """Poll for a receipt up to `attempts * interval` seconds."""
    for _ in range(attempts):
        try:
            receipt = await asyncio.to_thread(w3.eth.get_transaction_receipt, tx_hash)
            if receipt is not None:
                return dict(receipt)
        except Exception:
            pass
        await asyncio.sleep(interval)
    return None


# Expose chain_service as a namespace object for services that expect an object
class _ChainService:
    """Namespace object exposing chain functions as attributes."""
    is_connected = staticmethod(is_connected)
    get_balance = staticmethod(get_balance)
    get_block_number = staticmethod(get_block_number)
    get_transaction = staticmethod(get_transaction)
    get_transaction_receipt = staticmethod(get_transaction_receipt)
    get_block = staticmethod(get_block)
    get_gas_price = staticmethod(get_gas_price)
    send_raw_transaction = staticmethod(send_raw_transaction)
    estimate_gas = staticmethod(estimate_gas)
    get_nonce = staticmethod(get_nonce)
    send_native = staticmethod(send_native)
    wait_for_receipt = staticmethod(wait_for_receipt)


chain_service = _ChainService()
