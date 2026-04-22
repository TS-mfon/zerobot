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
    """Provide the user with a link to the 0G testnet faucet."""
    tid = update.effective_user.id

    try:
        user = await get_user(tid)

        text = "0G Testnet Faucet\n\n"

        if user and user.wallet_address:
            text += (
                f"Your wallet address:\n`{user.wallet_address}`\n\n"
                f"Visit the faucet to claim testnet A0GI tokens:\n"
                f"{settings.og_faucet_url}\n\n"
                "Copy your address above and paste it on the faucet page."
            )
        else:
            text += (
                "You don't have a wallet yet.\n"
                "Use /connect to create one, then come back here to get testnet tokens.\n\n"
                f"Faucet URL: {settings.og_faucet_url}"
            )

        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as exc:
        logger.exception("Error in /faucet")
        await update.message.reply_text(error_message(str(exc)))
