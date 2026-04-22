"""Handler for the /stake command."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings
from bot.services.wallet_service import get_user
from bot.utils.formatting import error_message, link

logger = logging.getLogger(__name__)


async def stake_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show staking information and links for the 0G network."""
    tid = update.effective_user.id

    try:
        user = await get_user(tid)

        text = (
            "0G Staking Information\n\n"
            "Staking on the 0G network allows you to secure the chain "
            "and earn rewards.\n\n"
        )

        if user and user.wallet_address:
            text += f"Your wallet: `{user.wallet_address}`\n\n"
        else:
            text += "Connect a wallet first with /connect to see your staking status.\n\n"

        text += (
            "Staking is currently available through the 0G web portal.\n"
            f"Explorer: {settings.og_explorer_url}\n\n"
            "_On-chain staking delegation via the bot is coming soon._"
        )

        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as exc:
        logger.exception("Error in /stake")
        await update.message.reply_text(error_message(str(exc)))
