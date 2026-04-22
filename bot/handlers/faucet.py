"""Handler for the /faucet command."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import settings
from bot.services.wallet_service import get_user
from bot.utils.formatting import error_message

logger = logging.getLogger(__name__)


async def faucet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provide the user with instructions for funding their wallet on 0G mainnet."""
    tid = update.effective_user.id

    try:
        user = await get_user(tid)

        text = "0G Wallet Funding\n\n"

        if user and user.wallet_address:
            text += (
                f"Your wallet address:\n`{user.wallet_address}`\n\n"
                "ZeroBot is connected to 0G mainnet.\n"
                "Send A0GI tokens to the address above to fund your wallet.\n\n"
                "You can acquire A0GI from supported exchanges or bridges.\n"
                f"Explorer: {settings.og_explorer_url}"
            )
        else:
            text += (
                "You don't have a wallet yet.\n"
                "Use /connect to create one, then fund it with A0GI tokens."
            )

        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as exc:
        logger.exception("Error in /faucet")
        await update.message.reply_text(error_message(str(exc)))
