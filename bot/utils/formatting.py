"""Telegram message formatting helpers."""

from __future__ import annotations

from typing import Optional


def mono(text: str) -> str:
    """Wrap *text* in Telegram monospace (code) markup."""
    return f"`{text}`"


def bold(text: str) -> str:
    """Wrap *text* in Telegram bold markup (MarkdownV2-safe)."""
    return f"*{text}*"


def link(label: str, url: str) -> str:
    """Return an inline link in Markdown format."""
    return f"[{label}]({url})"


def address_short(address: str) -> str:
    """Shorten an Ethereum-style address for display: 0x1234...abcd."""
    if len(address) > 12:
        return f"{address[:6]}...{address[-4:]}"
    return address


def format_balance(wei: int, symbol: str = "A0GI", decimals: int = 18) -> str:
    """Convert a wei-denominated balance to a human-readable string."""
    value = wei / (10 ** decimals)
    return f"{value:,.6f} {symbol}"


def tx_link(tx_hash: str, explorer_url: str) -> str:
    """Return a clickable explorer link for a transaction hash."""
    short = address_short(tx_hash)
    return f"[{short}]({explorer_url}/tx/{tx_hash})"


def error_message(msg: str, hint: Optional[str] = None) -> str:
    """Return a consistently formatted error message."""
    text = f"Something went wrong: {msg}"
    if hint:
        text += f"\n\nHint: {hint}"
    return text
