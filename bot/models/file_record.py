"""File record data model for 0G storage uploads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FileRecord:
    id: Optional[int] = None
    telegram_id: int = 0
    file_name: str = ""
    file_hash: str = ""
    file_size: int = 0
    uploaded_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "FileRecord":
        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            file_name=row["file_name"],
            file_hash=row["file_hash"],
            file_size=row["file_size"],
            uploaded_at=row["uploaded_at"],
        )
