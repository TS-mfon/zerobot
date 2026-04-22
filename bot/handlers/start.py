"""Handlers for /start and /help commands."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

WELCOME_TEXT = """<b>Welcome to ZeroBot</b> - your gateway to the 0G ecosystem!

Here is what I can do:

<b>Wallet</b>
/connect - Create or view your 0G wallet
/balance - Check your A0GI balance
/portfolio - View your full portfolio

<b>Storage</b>
/store - Upload a file to 0G Storage
/retrieve - Retrieve a file by hash
/files - List your uploaded files

<b>Compute</b>
/buy_compute - Purchase GPU compute
/job_status - Check a compute job

<b>Staking</b>
/stake - View staking information

<b>Explorer</b>
/explorer - Latest block info
/tx - Look up a transaction

<b>Market</b>
/prices - Current token prices
/alerts - Manage price alerts

<b>Misc</b>
/faucet - Get testnet tokens
/help - Show this message"""


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    logger.info("/start from user %s", update.effective_user.id)
    await update.message.reply_text(WELCOME_TEXT, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command (same output as /start)."""
    logger.info("/help from user %s", update.effective_user.id)
    await update.message.reply_text(WELCOME_TEXT, parse_mode="HTML")
