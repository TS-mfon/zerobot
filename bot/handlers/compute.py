"""Handlers for /buy_compute, /job_status, and compute inline callbacks."""

from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services.compute_service import buy_compute, confirm_compute_purchase, get_job_status
from bot.services.wallet_service import get_user, has_wallet, require_balance
from bot.utils.formatting import error_message

logger = logging.getLogger(__name__)


async def buy_compute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initiate a compute purchase on the 0G marketplace."""
    tid = update.effective_user.id

    try:
        if not await has_wallet(tid):
            await update.message.reply_text(
                "You need a wallet first. Use /connect to create one."
            )
            return

        # Balance gate -- user must have funded their wallet
        user = await get_user(tid)
        has_funds = await require_balance(tid)
        if not has_funds:
            await update.message.reply_text(
                "Insufficient balance!\n\n"
                "Please fund your wallet first:\n"
                f"Address: <code>{user.wallet_address}</code>\n\n"
                "Send A0GI tokens to this address, then try again.",
                parse_mode="HTML",
            )
            return

        # Parse optional arguments: /buy_compute [gpu_type] [hours]
        gpu_type = "A100"
        hours = 1
        if context.args:
            if len(context.args) >= 1:
                gpu_type = context.args[0].upper()
            if len(context.args) >= 2:
                try:
                    hours = int(context.args[1])
                except ValueError:
                    await update.message.reply_text("Hours must be a number.")
                    return

        job = await buy_compute(tid, gpu_type=gpu_type, duration_hours=hours)

        # Store pending job info in user_data so the callback can retrieve it
        context.user_data["pending_compute_job"] = {
            "job_id": job.job_id,
            "gpu_type": job.gpu_type,
            "duration_hours": job.duration_hours,
            "cost_a0gi": job.cost_a0gi,
        }

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Confirm", callback_data=f"compute_confirm:{job.job_id}"),
                    InlineKeyboardButton("Cancel", callback_data="compute_cancel"),
                ]
            ]
        )

        await update.message.reply_text(
            f"Compute Purchase Request\n\n"
            f"GPU: {job.gpu_type}\n"
            f"Duration: {job.duration_hours}h\n"
            f"Estimated cost: {job.cost_a0gi} A0GI\n\n"
            f"Confirm this purchase?",
            reply_markup=keyboard,
        )
    except Exception as exc:
        logger.exception("Error in /buy_compute")
        await update.message.reply_text(error_message(str(exc)))


async def buy_compute_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Confirm / Cancel inline button presses for compute purchases."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    tid = update.effective_user.id

    try:
        if data == "compute_cancel":
            await query.edit_message_text("Purchase cancelled.")
            # Clean up stored pending job
            context.user_data.pop("pending_compute_job", None)
            return

        if data.startswith("compute_confirm:"):
            job_id = data.split(":", 1)[1]

            # Re-verify balance before executing the real transaction
            user = await get_user(tid)
            has_funds = await require_balance(tid)
            if not has_funds:
                await query.edit_message_text(
                    "Insufficient balance!\n\n"
                    f"Please fund your wallet:\n{user.wallet_address}\n\n"
                    "Send A0GI tokens, then try /buy_compute again."
                )
                context.user_data.pop("pending_compute_job", None)
                return

            await query.edit_message_text("Processing your compute purchase...")

            # Execute the actual on-chain purchase
            result = await confirm_compute_purchase(tid, job_id)

            await query.edit_message_text(
                f"Compute purchase confirmed!\n\n"
                f"Job ID: {result.job_id}\n"
                f"Status: {result.status}\n"
                f"GPU: {result.gpu_type}\n"
                f"Duration: {result.duration_hours}h\n"
                f"Cost: {result.cost_a0gi} A0GI\n\n"
                f"Use /job_status {result.job_id} to track progress."
            )
            context.user_data.pop("pending_compute_job", None)
            return

    except Exception as exc:
        logger.exception("Error in compute callback")
        await query.edit_message_text(error_message(str(exc)))


async def job_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check the status of a compute job."""
    try:
        if not context.args:
            await update.message.reply_text(
                "Usage: /job_status <job_id>\n\nExample: /job_status job_placeholder_001"
            )
            return

        job_id = context.args[0]
        job = await get_job_status(job_id)

        if job is None:
            await update.message.reply_text("No job found with that ID.")
            return

        status_emoji_map = {
            "pending": "Pending",
            "running": "Running",
            "completed": "Completed",
            "failed": "Failed",
        }
        status_label = status_emoji_map.get(job.status, job.status)

        await update.message.reply_text(
            f"Job Status\n\n"
            f"ID: `{job.job_id}`\n"
            f"Status: {status_label}\n"
            f"GPU: {job.gpu_type}\n"
            f"Duration: {job.duration_hours}h\n"
            f"Cost: {job.cost_a0gi} A0GI",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.exception("Error in /job_status")
        await update.message.reply_text(error_message(str(exc)))
