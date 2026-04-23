"""ZeroBot entry point -- boots the Telegram bot application."""

import logging
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.config import settings
from bot.db.database import init_db
from bot.utils.logging_config import setup_logging

# Handler imports
from bot.handlers.start import start_command, help_command
from bot.handlers.wallet import connect_command, balance_command, portfolio_command
from bot.handlers.storage import store_command, retrieve_command, files_command
from bot.handlers.compute import buy_compute_command, buy_compute_callback, job_status_command
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
    logger.info("Database initialized.")


def main() -> None:
    """Build application, register handlers, and start polling."""
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(_post_init)
        .build()
    )

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

    # Callback handler for inline Confirm/Cancel buttons
    app.add_handler(CallbackQueryHandler(buy_compute_callback, pattern=r"^compute_"))

    logger.info("ZeroBot starting...")
    app.run_polling(drop_pending_updates=True)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status":"ok","bot":"zerobot"}')

    def log_message(self, *args):
        pass  # suppress


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    # Start health server in background thread (for Render)
    threading.Thread(target=start_health_server, daemon=True).start()
    main()
