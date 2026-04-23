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
            "cost_og": job.cost_og,
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
            f"<b>Compute Purchase Request</b>\n\n"
            f"GPU: {job.gpu_type}\n"
            f"Duration: {job.duration_hours}h\n"
            f"Estimated cost: {job.cost_og} OG\n\n"
            f"Confirm this purchase? An on-chain transaction will be broadcast.",
            reply_markup=keyboard,
            parse_mode="HTML",
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

            # Retrieve stored job info for the purchase
            pending = context.user_data.get("pending_compute_job") or {}
            gpu_type = pending.get("gpu_type", "A100")
            hours = pending.get("duration_hours", 1)

            await query.edit_message_text("⏳ Broadcasting transaction on 0G mainnet...")

            result = await confirm_compute_purchase(
                telegram_id=tid,
                job_id=job_id,
                gpu_type=gpu_type,
                duration_hours=hours,
            )

            if result.status == "failed":
                await query.edit_message_text(
                    f"❌ <b>Purchase failed.</b>\n\n"
                    f"This usually means the compute provider address isn't configured, "
                    f"or there was a network error. Contact support or try again later.",
                    parse_mode="HTML",
                )
            else:
                msg = (
                    f"✅ <b>Compute purchase submitted!</b>\n\n"
                    f"Job ID: <code>{result.job_id}</code>\n"
                    f"Status: {result.status}\n"
                    f"GPU: {result.gpu_type}\n"
                    f"Duration: {result.duration_hours}h\n"
                    f"Cost: {result.cost_og} OG\n"
                )
                if result.tx_hash:
                    msg += f"Tx: <code>{result.tx_hash}</code>\n"
                msg += f"\nUse /job_status {result.job_id} to check progress."
                await query.edit_message_text(msg, parse_mode="HTML")
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
            f"<b>Job Status</b>\n\n"
            f"ID: <code>{job.job_id}</code>\n"
            f"Status: {status_label}\n"
            f"GPU: {job.gpu_type}\n"
            f"Duration: {job.duration_hours}h\n"
            f"Cost: {job.cost_og} OG",
            parse_mode="HTML",
        )
    except Exception as exc:
        logger.exception("Error in /job_status")
        await update.message.reply_text(error_message(str(exc)))
