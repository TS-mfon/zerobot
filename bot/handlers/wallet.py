"""Handlers for /connect, /balance, and /portfolio commands."""

from __future__ import annotations

import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services.wallet_service import create_wallet, get_user, has_wallet
from bot.services.chain_service import get_balance
from bot.utils.formatting import address_short, format_balance, error_message

logger = logging.getLogger(__name__)


async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create or display the user's embedded 0G wallet."""
    tid = update.effective_user.id
    username = update.effective_user.username

    try:
        if await has_wallet(tid):
            user = await get_user(tid)
            await update.message.reply_text(
                f"You already have a wallet connected.\n\n"
                f"Address: `{user.wallet_address}`\n\n"
                f"Use /balance to check your balance.",
                parse_mode="Markdown",
            )
            return

        address, private_key = await create_wallet(tid, username)
        await update.message.reply_text(
            f"Your new 0G wallet has been created.\n\n"
            f"Address: `{address}`\n\n"
            f"Private Key (save this, shown only once):\n"
            f"||`{private_key}`||\n\n"
            f"Your private key is encrypted and stored securely. "
            f"Use /balance to check your balance.",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.exception("Error in /connect")
        await update.message.reply_text(error_message(str(exc)))


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the native A0GI balance for the user's wallet."""
    tid = update.effective_user.id

    try:
        user = await get_user(tid)
        if user is None or user.wallet_address is None:
            await update.message.reply_text(
                "You don't have a wallet yet. Use /connect to create one."
            )
            return

        balance_wei = await asyncio.to_thread(get_balance, user.wallet_address)
        readable = format_balance(balance_wei)
        short_addr = address_short(user.wallet_address)
        await update.message.reply_text(
            f"Wallet: `{short_addr}`\n"
            f"Balance: *{readable}*",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.exception("Error in /balance")
        await update.message.reply_text(
            error_message(str(exc), hint="The 0G RPC node may be temporarily unavailable.")
        )


async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the user's portfolio overview."""
    tid = update.effective_user.id

    try:
        user = await get_user(tid)
        if user is None or user.wallet_address is None:
            await update.message.reply_text(
                "You don't have a wallet yet. Use /connect to create one."
            )
            return

        balance_wei = await asyncio.to_thread(get_balance, user.wallet_address)
        readable = format_balance(balance_wei)

        text = (
            f"Portfolio for `{address_short(user.wallet_address)}`\n"
            f"{'=' * 30}\n"
            f"A0GI (Native): *{readable}*\n\n"
            f"_Token tracking for ERC-20s will be available soon._"
        )
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as exc:
        logger.exception("Error in /portfolio")
        await update.message.reply_text(error_message(str(exc)))
