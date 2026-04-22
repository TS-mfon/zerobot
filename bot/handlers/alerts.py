"""Handler for the /alerts command."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.alert_service import create_alert, list_alerts, delete_alert
from bot.utils.formatting import error_message

logger = logging.getLogger(__name__)


async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage price / node alerts.

    Usage:
        /alerts                     -- list active alerts
        /alerts add price 0.05      -- alert when price crosses 0.05
        /alerts remove <id>         -- remove an alert
    """
    tid = update.effective_user.id

    try:
        # No arguments -- list alerts
        if not context.args:
            user_alerts = await list_alerts(tid)
            if not user_alerts:
                await update.message.reply_text(
                    "You have no active alerts.\n\n"
                    "Create one with:\n"
                    "/alerts add price <threshold>\n\n"
                    "Example: /alerts add price 0.05"
                )
                return

            lines = ["Your active alerts:\n"]
            for a in user_alerts:
                lines.append(
                    f"  ID {a.id}: {a.alert_type} -- threshold {a.threshold}"
                )
            await update.message.reply_text("\n".join(lines))
            return

        subcommand = context.args[0].lower()

        # Add a new alert
        if subcommand == "add":
            if len(context.args) < 3:
                await update.message.reply_text(
                    "Usage: /alerts add <type> <threshold>\n\nExample: /alerts add price 0.05"
                )
                return

            alert_type = context.args[1]
            try:
                threshold = float(context.args[2])
            except ValueError:
                await update.message.reply_text("Threshold must be a number.")
                return

            alert = await create_alert(tid, alert_type, threshold)
            await update.message.reply_text(
                f"Alert created (ID {alert.id}).\n"
                f"Type: {alert.alert_type}\n"
                f"Threshold: {alert.threshold}"
            )
            return

        # Remove an alert
        if subcommand == "remove":
            if len(context.args) < 2:
                await update.message.reply_text("Usage: /alerts remove <alert_id>")
                return

            try:
                alert_id = int(context.args[1])
            except ValueError:
                await update.message.reply_text("Alert ID must be a number.")
                return

            await delete_alert(alert_id)
            await update.message.reply_text(f"Alert {alert_id} removed.")
            return

        await update.message.reply_text(
            "Unknown subcommand. Use /alerts, /alerts add, or /alerts remove."
        )
    except Exception as exc:
        logger.exception("Error in /alerts")
        await update.message.reply_text(error_message(str(exc)))
