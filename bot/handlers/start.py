"""Handlers for /start and /help commands."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "Welcome to *ZeroBot* -- your gateway to the 0G ecosystem\\!\n\n"
    "Here is what I can do:\n\n"
    "*Wallet*\n"
    "/connect \\- Create or view your 0G wallet\n"
    "/balance \\- Check your A0GI balance\n"
    "/portfolio \\- View your full portfolio\n\n"
    "*Storage*\n"
    "/store \\- Upload a file to 0G Storage\n"
    "/retrieve \\- Retrieve a file by hash\n"
    "/files \\- List your uploaded files\n\n"
    "*Compute*\n"
    "/buy\\_compute \\- Purchase GPU compute\n"
    "/job\\_status \\- Check a compute job\n\n"
    "*Staking*\n"
    "/stake \\- View staking information\n\n"
    "*Explorer*\n"
    "/explorer \\- Latest block info\n"
    "/tx \\<hash\\> \\- Look up a transaction\n\n"
    "*Market*\n"
    "/prices \\- Current token prices\n"
    "/alerts \\- Manage price alerts\n\n"
    "*Misc*\n"
    "/faucet \\- Get testnet tokens\n"
    "/help \\- Show this message\n"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    logger.info("/start from user %s", update.effective_user.id)
    await update.message.reply_text(WELCOME_TEXT, parse_mode="MarkdownV2")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command (same output as /start)."""
    logger.info("/help from user %s", update.effective_user.id)
    await update.message.reply_text(WELCOME_TEXT, parse_mode="MarkdownV2")
