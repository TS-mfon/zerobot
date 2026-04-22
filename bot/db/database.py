"""Async SQLite database helpers using aiosqlite."""

from __future__ import annotations

import aiosqlite

from bot.config import settings

DB_PATH = settings.database_path


async def get_db() -> aiosqlite.Connection:
    """Return an open aiosqlite connection (caller must close)."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    """Create tables if they do not yet exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id   INTEGER PRIMARY KEY,
                username      TEXT,
                wallet_address TEXT,
                encrypted_key TEXT,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS file_records (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id   INTEGER NOT NULL,
                file_name     TEXT NOT NULL,
                file_hash     TEXT NOT NULL,
                file_size     INTEGER DEFAULT 0,
                uploaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tx_hash       TEXT,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
            """
        )
        # Migration: add tx_hash column to existing file_records tables
        try:
            await db.execute(
                "ALTER TABLE file_records ADD COLUMN tx_hash TEXT"
            )
        except Exception:
            # Column already exists -- safe to ignore
            pass
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id   INTEGER NOT NULL,
                alert_type    TEXT NOT NULL,
                threshold     REAL,
                is_active     INTEGER DEFAULT 1,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
            """
        )
        await db.commit()
