"""0G decentralised storage interaction layer.

Uploads files to the 0G storage network via the storage indexer API.
File metadata is also persisted locally in SQLite for quick lookups.
"""

from __future__ import annotations

import hashlib
import logging
from typing import List, Optional

import httpx

from bot.config import settings
from bot.db.database import get_db
from bot.models.file_record import FileRecord
from bot.services.chain_service import send_contract_transaction
from bot.services.compute_service import ZEROBOT_CONTRACT_ABI
from bot.services.wallet_service import get_private_key, get_user

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 0G Storage Indexer interaction
# ---------------------------------------------------------------------------

async def _upload_to_0g_storage(file_data: bytes, file_name: str) -> dict:
    """Upload *file_data* to the 0G decentralised storage network.

    Uses the 0G storage indexer HTTP API.  Returns a dict with
    ``root_hash``, ``tx_hash``, and ``size``.

    Raises on failure so that callers surface real errors to users.
    """
    indexer_url = settings.og_storage_indexer.rstrip("/")

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Attempt upload via the indexer's file upload endpoint
        response = await client.post(
            f"{indexer_url}/api/v1/file/upload",
            files={"file": (file_name, file_data)},
        )
        response.raise_for_status()
        result = response.json()

    root_hash = result.get("root") or result.get("root_hash", "")
    tx_hash = result.get("tx_hash") or result.get("tx", "")

    if not root_hash and not tx_hash:
        # The indexer may use a different response shape -- log for debugging
        logger.warning("Unexpected 0G storage response: %s", result)

    return {
        "root_hash": root_hash,
        "tx_hash": tx_hash,
        "size": len(file_data),
    }


# ---------------------------------------------------------------------------
# Public helpers used by handlers
# ---------------------------------------------------------------------------

async def store_file(
    telegram_id: int,
    file_name: str,
    file_data: bytes,
) -> FileRecord:
    """Upload *file_data* to 0G storage and persist metadata locally."""

    # Real upload to 0G storage
    upload_result = await _upload_to_0g_storage(file_data, file_name)

    # Use the root hash from 0G; fall back to local SHA-256 only as an
    # identifier for the local DB if the indexer didn't return one.
    file_hash = upload_result["root_hash"] or hashlib.sha256(file_data).hexdigest()
    tx_hash = upload_result["tx_hash"]
    file_size = upload_result["size"]

    db = await get_db()
    try:
        cursor = await db.execute(
            """
            INSERT INTO file_records (telegram_id, file_name, file_hash, file_size, tx_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (telegram_id, file_name, file_hash, file_size, tx_hash),
        )
        await db.commit()
        record_id = cursor.lastrowid
    finally:
        await db.close()

    return FileRecord(
        id=record_id,
        telegram_id=telegram_id,
        file_name=file_name,
        file_hash=file_hash,
        file_size=file_size,
        tx_hash=tx_hash,
    )


async def anchor_file_onchain(telegram_id: int, file_hash: str, file_name: str) -> Optional[str]:
    """Anchor a storage root on the ZeroBot registry contract when configured."""
    contract_address = settings.zerobot_contract_address.strip()
    if not contract_address:
        return None

    user = await get_user(telegram_id)
    if user is None or user.wallet_address is None:
        return None

    private_key = await get_private_key(telegram_id)
    if not private_key:
        return None

    return await send_contract_transaction(
        private_key=private_key,
        from_address=user.wallet_address,
        contract_address=contract_address,
        abi=ZEROBOT_CONTRACT_ABI,
        function_name="anchorStorage",
        args=[file_hash, file_name],
        value_og=0.0,
    )


async def retrieve_file(file_hash: str) -> Optional[FileRecord]:
    """Look up a file record by its hash."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM file_records WHERE file_hash = ?", (file_hash,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return FileRecord.from_row(row)
    finally:
        await db.close()


async def list_files(telegram_id: int) -> List[FileRecord]:
    """Return all files uploaded by a given user."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM file_records WHERE telegram_id = ? ORDER BY uploaded_at DESC",
            (telegram_id,),
        )
        rows = await cursor.fetchall()
        return [FileRecord.from_row(r) for r in rows]
    finally:
        await db.close()
