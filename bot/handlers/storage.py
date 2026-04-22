"""Handlers for /store, /retrieve, and /files commands."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.services.storage_service import store_file, retrieve_file, list_files
from bot.services.wallet_service import has_wallet
from bot.utils.formatting import error_message

logger = logging.getLogger(__name__)


async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Upload a file to 0G storage.

    The user should reply to a document with /store, or send a document
    in the same message.
    """
    tid = update.effective_user.id

    try:
        if not await has_wallet(tid):
            await update.message.reply_text(
                "You need a wallet first. Use /connect to create one."
            )
            return

        doc = update.message.document or (
            update.message.reply_to_message
            and update.message.reply_to_message.document
        )

        if doc is None:
            await update.message.reply_text(
                "Please send a file (as a document) or reply to a file with /store."
            )
            return

        status_msg = await update.message.reply_text("Uploading to 0G Storage...")

        tg_file = await doc.get_file()
        file_bytes = await tg_file.download_as_bytearray()
        record = await store_file(tid, doc.file_name or "unnamed", bytes(file_bytes))

        await status_msg.edit_text(
            f"File stored successfully.\n\n"
            f"Name: `{record.file_name}`\n"
            f"Hash: `{record.file_hash}`\n"
            f"Size: {record.file_size:,} bytes\n\n"
            f"Use /retrieve `{record.file_hash}` to retrieve it.",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.exception("Error in /store")
        await update.message.reply_text(error_message(str(exc)))


async def retrieve_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Look up a stored file by its hash."""
    tid = update.effective_user.id

    try:
        if not context.args:
            await update.message.reply_text(
                "Usage: /retrieve <file_hash>\n\nExample: /retrieve abc123..."
            )
            return

        file_hash = context.args[0]
        record = await retrieve_file(file_hash)

        if record is None:
            await update.message.reply_text(
                "No file found with that hash. Double-check and try again."
            )
            return

        await update.message.reply_text(
            f"File found.\n\n"
            f"Name: `{record.file_name}`\n"
            f"Hash: `{record.file_hash}`\n"
            f"Size: {record.file_size:,} bytes\n"
            f"Uploaded: {record.uploaded_at}",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.exception("Error in /retrieve")
        await update.message.reply_text(error_message(str(exc)))


async def files_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all files uploaded by the user."""
    tid = update.effective_user.id

    try:
        records = await list_files(tid)
        if not records:
            await update.message.reply_text(
                "You haven't uploaded any files yet. Use /store to upload one."
            )
            return

        lines = ["Your stored files:\n"]
        for i, rec in enumerate(records, start=1):
            lines.append(
                f"{i}. `{rec.file_name}` -- {rec.file_size:,} bytes\n"
                f"   Hash: `{rec.file_hash}`"
            )

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as exc:
        logger.exception("Error in /files")
        await update.message.reply_text(error_message(str(exc)))
