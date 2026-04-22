"""ZeroBot entry point -- boots the Telegram bot application."""

import asyncio
import logging

from telegram.ext import ApplicationBuilder, CommandHandler

from bot.config import settings
from bot.db.database import init_db

# Handler imports
from bot.handlers.start import start_command, help_command
from bot.handlers.wallet import connect_command, balance_command, portfolio_command
from bot.handlers.storage import store_command, retrieve_command, files_command
from bot.handlers.compute import buy_compute_command, job_status_command
from bot.handlers.staking import stake_command
from bot.handlers.explorer import explorer_command, tx_command
from bot.handlers.alerts import alerts_command
from bot.handlers.prices import prices_command
from bot.handlers.faucet import faucet_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Build application, register handlers, and start polling."""

    # Initialise the database before the bot starts polling
    asyncio.run(init_db())

    app = ApplicationBuilder().token(settings.telegram_bot_token).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("connect", connect_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("store", store_command))
    app.add_handler(CommandHandler("retrieve", retrieve_command))
    app.add_handler(CommandHandler("files", files_command))
    app.add_handler(CommandHandler("buy_compute", buy_compute_command))
    app.add_handler(CommandHandler("job_status", job_status_command))
    app.add_handler(CommandHandler("stake", stake_command))
    app.add_handler(CommandHandler("explorer", explorer_command))
    app.add_handler(CommandHandler("tx", tx_command))
    app.add_handler(CommandHandler("prices", prices_command))
    app.add_handler(CommandHandler("alerts", alerts_command))
    app.add_handler(CommandHandler("faucet", faucet_command))

    logger.info("ZeroBot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
