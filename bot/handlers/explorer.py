"""Handlers for /explorer and /tx commands."""

from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings
from bot.services.chain_service import get_block_number, get_block, get_transaction
from bot.utils.formatting import address_short, error_message, tx_link

logger = logging.getLogger(__name__)


async def explorer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the latest block information from the 0G chain."""
    try:
        block_num = await asyncio.to_thread(get_block_number)
        block = await asyncio.to_thread(get_block, block_num)

        if block is None:
            await update.message.reply_text("Could not fetch the latest block.")
            return

        tx_count = len(block.get("transactions", []))
        timestamp = block.get("timestamp", "N/A")
        gas_used = block.get("gasUsed", 0)
        gas_limit = block.get("gasLimit", 0)

        text = (
            f"0G Chain Explorer\n\n"
            f"Latest Block: `{block_num}`\n"
            f"Timestamp: {timestamp}\n"
            f"Transactions: {tx_count}\n"
            f"Gas Used: {gas_used:,} / {gas_limit:,}\n\n"
            f"View on explorer: {settings.og_explorer_url}/block/{block_num}"
        )

        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as exc:
        logger.exception("Error in /explorer")
        await update.message.reply_text(
            error_message(str(exc), hint="The 0G RPC node may be temporarily unavailable.")
        )


async def tx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Look up a transaction by hash."""
    try:
        if not context.args:
            await update.message.reply_text(
                "Usage: /tx <transaction_hash>\n\nExample: /tx 0xabc123..."
            )
            return

        tx_hash = context.args[0]
        tx = await asyncio.to_thread(get_transaction, tx_hash)

        if tx is None:
            await update.message.reply_text(
                "Transaction not found. Make sure the hash is correct."
            )
            return

        from_addr = address_short(str(tx.get("from", "")))
        to_addr = address_short(str(tx.get("to", ""))) if tx.get("to") else "Contract Creation"
        value_wei = tx.get("value", 0)
        value_a0gi = value_wei / 10**18
        gas = tx.get("gas", 0)
        block = tx.get("blockNumber", "Pending")

        text = (
            f"Transaction Details\n\n"
            f"Hash: `{address_short(tx_hash)}`\n"
            f"Block: {block}\n"
            f"From: `{from_addr}`\n"
            f"To: `{to_addr}`\n"
            f"Value: {value_a0gi:,.6f} A0GI\n"
            f"Gas: {gas:,}\n\n"
            f"View: {settings.og_explorer_url}/tx/{tx_hash}"
        )

        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as exc:
        logger.exception("Error in /tx")
        await update.message.reply_text(error_message(str(exc)))
