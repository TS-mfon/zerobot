"""0G decentralised storage interaction layer.

The 0G storage SDK is still evolving.  This module provides a placeholder
implementation that records file metadata locally and will be wired to the
real SDK once it stabilises.
"""

from __future__ import annotations

import hashlib
import logging
from typing import List, Optional

from bot.db.database import get_db
from bot.models.file_record import FileRecord

logger = logging.getLogger(__name__)


async def store_file(
    telegram_id: int,
    file_name: str,
    file_data: bytes,
) -> FileRecord:
    """Simulate uploading *file_data* to 0G storage.

    In production this would call the 0G storage SDK.  For the MVP we
    compute a SHA-256 hash and persist the record in SQLite.
    """
    file_hash = hashlib.sha256(file_data).hexdigest()
    file_size = len(file_data)

    db = await get_db()
    try:
        cursor = await db.execute(
            """
            INSERT INTO file_records (telegram_id, file_name, file_hash, file_size)
            VALUES (?, ?, ?, ?)
            """,
            (telegram_id, file_name, file_hash, file_size),
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
