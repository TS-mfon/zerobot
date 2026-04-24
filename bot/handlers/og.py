"""Handlers for live 0G stack and compute CLI discovery."""

from __future__ import annotations

import html
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.og_compute_cli import (
    get_account_status,
    get_network_status,
    get_stack_summary,
    list_compute_providers,
    list_model_catalog,
)
from bot.utils.formatting import error_message

logger = logging.getLogger(__name__)


async def stack_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        text = await get_stack_summary()
        await update.message.reply_text(text)
    except Exception as exc:
        logger.exception("Error in /stack")
        await update.message.reply_text(error_message(str(exc)))


async def compute_market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        output = await list_compute_providers()
        await update.message.reply_text(
            f"0G Compute mainnet providers\n\n<pre>{html.escape(output[:3500])}</pre>",
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("Error in /compute_market")
        await update.message.reply_text(error_message(str(exc), "Check that the 0G Compute CLI is reachable from Render."))


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        output = await list_model_catalog()
        await update.message.reply_text(
            f"0G model catalog\n\n<pre>{html.escape(output[:3500])}</pre>",
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("Error in /models")
        await update.message.reply_text(error_message(str(exc)))


async def compute_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        network = await get_network_status()
        account = await get_account_status()
        await update.message.reply_text(
            f"0G Compute CLI status\n\n<pre>{html.escape(network[:1500])}\n\n{html.escape(account[:1800])}</pre>",
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("Error in /compute_account")
        await update.message.reply_text(error_message(str(exc)))
