"""Wallet creation and management with Fernet-encrypted private keys."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Tuple

from eth_account import Account

from bot.db.database import get_db
from bot.models.user import User
from bot.utils.encryption import encrypt, decrypt

logger = logging.getLogger(__name__)


async def get_user(telegram_id: int) -> Optional[User]:
    """Look up a user by Telegram ID."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return User.from_row(row)
    finally:
        await db.close()


async def create_wallet(telegram_id: int, username: Optional[str] = None) -> Tuple[str, str]:
    """Create a new Ethereum-compatible wallet for a user.

    Returns (wallet_address, private_key) -- the private key is shown once
    to the user and then stored only in encrypted form.
    """
    account = Account.create()
    address = account.address
    private_key = account.key.hex()
    encrypted_pk = encrypt(private_key)

    db = await get_db()
    try:
        await db.execute(
            """
            INSERT INTO users (telegram_id, username, wallet_address, encrypted_key)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                wallet_address = excluded.wallet_address,
                encrypted_key  = excluded.encrypted_key,
                username       = excluded.username
            """,
            (telegram_id, username, address, encrypted_pk),
        )
        await db.commit()
    finally:
        await db.close()

    return address, private_key


async def get_private_key(telegram_id: int) -> Optional[str]:
    """Retrieve and decrypt the private key for *telegram_id*."""
    user = await get_user(telegram_id)
    if user is None or user.encrypted_key is None:
        return None
    return decrypt(user.encrypted_key)


async def has_wallet(telegram_id: int) -> bool:
    """Return True if the user already has a connected wallet."""
    user = await get_user(telegram_id)
    return user is not None and user.wallet_address is not None


async def require_balance(telegram_id: int, min_amount_wei: int = 0) -> bool:
    """Check that the user's wallet has been funded.

    Returns ``False`` when the wallet does not exist or has insufficient
    balance (i.e. balance <= *min_amount_wei*).
    """
    # Import lazily to avoid circular / heavy-import issues at module load
    from bot.services.chain_service import get_balance

    user = await get_user(telegram_id)
    if user is None or user.wallet_address is None:
        return False
    balance = await asyncio.to_thread(get_balance, user.wallet_address)
    return balance > min_amount_wei
