"""Handler for the /prices command."""

from __future__ import annotations

import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.chain_service import get_gas_price, get_block_number
from bot.utils.formatting import error_message

logger = logging.getLogger(__name__)


async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current token price info and network stats.

    Full price-feed integration (CoinGecko / DEX) is planned.  For now
    we show on-chain gas price and block height as a network health proxy.
    """
    try:
        gas_price_wei = await asyncio.to_thread(get_gas_price)
        block_number = await asyncio.to_thread(get_block_number)

        gas_gwei = gas_price_wei / 1e9

        text = (
            "0G Market Snapshot\n\n"
            f"Gas Price: {gas_gwei:,.4f} Gwei\n"
            f"Latest Block: {block_number:,}\n\n"
            "Price feed integration (CoinGecko, DEX) coming soon.\n"
            "Use /alerts to set up price notifications."
        )

        await update.message.reply_text(text)
    except Exception as exc:
        logger.exception("Error in /prices")
        await update.message.reply_text(
            error_message(str(exc), hint="The 0G RPC may be temporarily unavailable.")
        )
