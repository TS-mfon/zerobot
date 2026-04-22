"""User data model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    telegram_id: int
    username: Optional[str] = None
    wallet_address: Optional[str] = None
    encrypted_key: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            telegram_id=row["telegram_id"],
            username=row["username"],
            wallet_address=row["wallet_address"],
            encrypted_key=row["encrypted_key"],
            created_at=row["created_at"],
        )
