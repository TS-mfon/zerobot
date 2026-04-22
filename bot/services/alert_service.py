"""Price and node alert management."""

from __future__ import annotations

import logging
from typing import List

from bot.db.database import get_db
from bot.models.alert import Alert

logger = logging.getLogger(__name__)


async def create_alert(
    telegram_id: int,
    alert_type: str,
    threshold: float,
) -> Alert:
    """Create a new alert for the user."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            INSERT INTO alerts (telegram_id, alert_type, threshold)
            VALUES (?, ?, ?)
            """,
            (telegram_id, alert_type, threshold),
        )
        await db.commit()
        alert_id = cursor.lastrowid
    finally:
        await db.close()

    return Alert(
        id=alert_id,
        telegram_id=telegram_id,
        alert_type=alert_type,
        threshold=threshold,
    )


async def list_alerts(telegram_id: int) -> List[Alert]:
    """Return all active alerts for a user."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM alerts WHERE telegram_id = ? AND is_active = 1 ORDER BY created_at DESC",
            (telegram_id,),
        )
        rows = await cursor.fetchall()
        return [Alert.from_row(r) for r in rows]
    finally:
        await db.close()


async def delete_alert(alert_id: int) -> None:
    """Soft-delete an alert by marking it inactive."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE alerts SET is_active = 0 WHERE id = ?", (alert_id,)
        )
        await db.commit()
    finally:
        await db.close()
