"""Thin async wrapper around web3.py for the 0G EVM chain."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from web3 import Web3

from bot.config import settings

logger = logging.getLogger(__name__)

# Module-level Web3 instance (HTTP provider, synchronous under the hood but
# fast enough for RPC calls wrapped in asyncio.to_thread when needed).
w3 = Web3(Web3.HTTPProvider(settings.og_rpc_url))


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
