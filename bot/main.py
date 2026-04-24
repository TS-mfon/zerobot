"""ZeroBot entry point -- boots the Telegram bot application."""

import logging
import os

from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.config import settings
from bot.db.database import init_db
from bot.utils.logging_config import setup_logging

# Handler imports
from bot.handlers.start import start_command, help_command, commands_command, BOT_COMMANDS
from bot.handlers.wallet import connect_command, balance_command, portfolio_command
from bot.handlers.storage import store_command, retrieve_command, files_command
from bot.handlers.compute import buy_compute_command, buy_compute_callback, job_status_command
from bot.handlers.og import (
    compute_account_command,
    compute_market_command,
    models_command,
    stack_command,
)
from bot.handlers.staking import stake_command
from bot.handlers.explorer import explorer_command, tx_command
from bot.handlers.alerts import alerts_command
from bot.handlers.prices import prices_command
from bot.handlers.faucet import faucet_command

setup_logging()
logger = logging.getLogger(__name__)


async def _post_init(application) -> None:
    """Run async initialization after the bot's event loop is set up."""
    await init_db()
    await application.bot.set_my_commands(
        [BotCommand(command, description) for command, description in BOT_COMMANDS]
    )
    logger.info("Database initialized.")


def _webhook_base_url() -> str:
    return (
        settings.webhook_base_url.strip()
        or os.environ.get("RENDER_EXTERNAL_URL", "").strip()
    )


def main() -> None:
    """Build application, register handlers, and start polling/webhook."""
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(_post_init)
        .build()
    )

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("commands", commands_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stack", stack_command))
    app.add_handler(CommandHandler("connect", connect_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("store", store_command))
    app.add_handler(CommandHandler("retrieve", retrieve_command))
    app.add_handler(CommandHandler("files", files_command))
    app.add_handler(CommandHandler("buy_compute", buy_compute_command))
    app.add_handler(CommandHandler("job_status", job_status_command))
    app.add_handler(CommandHandler("compute_market", compute_market_command))
    app.add_handler(CommandHandler("models", models_command))
    app.add_handler(CommandHandler("compute_account", compute_account_command))
    app.add_handler(CommandHandler("stake", stake_command))
    app.add_handler(CommandHandler("explorer", explorer_command))
    app.add_handler(CommandHandler("tx", tx_command))
    app.add_handler(CommandHandler("prices", prices_command))
    app.add_handler(CommandHandler("alerts", alerts_command))
    app.add_handler(CommandHandler("faucet", faucet_command))

    # Callback handler for inline Confirm/Cancel buttons
    app.add_handler(CallbackQueryHandler(buy_compute_callback, pattern=r"^compute_"))

    logger.info("ZeroBot starting...")
    webhook_base = _webhook_base_url()
    if webhook_base:
        token = settings.telegram_bot_token
        url_path = f"/telegram/{token}"
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", "10000")),
            url_path=url_path,
            webhook_url=f"{webhook_base}{url_path}",
            drop_pending_updates=True,
        )
        return

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
