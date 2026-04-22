"""Alert data model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Alert:
    id: Optional[int] = None
    telegram_id: int = 0
    alert_type: str = ""
    threshold: float = 0.0
    is_active: bool = True
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "Alert":
        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            alert_type=row["alert_type"],
            threshold=row["threshold"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )
