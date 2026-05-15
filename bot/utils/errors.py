"""User-facing Telegram error handling."""

from __future__ import annotations

import html
import logging
import traceback
from dataclasses import dataclass

from telegram import Update
from telegram.error import BadRequest, Forbidden, NetworkError, TimedOut
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ErrorGuide:
    title: str
    explanation: str
    next_steps: tuple[str, ...]


def support_code(error: BaseException) -> str:
    return hex(abs(hash((type(error).__name__, str(error)))) % 0xFFFFFF)[2:].upper().zfill(6)


def classify_error(error: BaseException) -> ErrorGuide:
    text = str(error).lower()

    if isinstance(error, (TimedOut, TimeoutError)) or "timeout" in text:
        return ErrorGuide(
            "Request timed out",
            "0G RPC, storage, compute, or Telegram did not respond before the timeout.",
            (
                "Retry the command in a minute.",
                "For /store, try a smaller file first.",
                "For compute commands, run /stack then /compute_market again.",
            ),
        )

    if isinstance(error, NetworkError) or "connection" in text or "rpc" in text or "dns" in text:
        return ErrorGuide(
            "0G network connection issue",
            "The bot could not reach one of the 0G services required for this command.",
            (
                "Retry shortly; RPC/indexer/provider endpoints can be temporarily unavailable.",
                "Run /stack to see the active 0G endpoints.",
                "If this was a transaction, check /balance before retrying.",
            ),
        )

    if isinstance(error, BadRequest):
        return ErrorGuide(
            "Telegram response formatting issue",
            "Telegram rejected the bot response, usually because it was too long or had unsupported formatting.",
            (
                "Retry with a shorter value.",
                "Use /commands to choose a more specific lookup.",
                "For transaction details, use /tx <hash>.",
            ),
        )

    if isinstance(error, Forbidden):
        return ErrorGuide(
            "Bot cannot reply here",
            "Telegram says the bot is not allowed to message this chat.",
            (
                "Open the bot directly and press Start.",
                "If this is a group, re-add the bot or allow messages.",
            ),
        )

    if isinstance(error, (ValueError, TypeError)) or "invalid" in text or "usage:" in text:
        return ErrorGuide(
            "Command format problem",
            "The command was missing a value or one value had the wrong format.",
            (
                "Run /commands for all supported commands.",
                "Use examples like /retrieve <root_hash> or /tx <hash>.",
                "For compute, use /buy_compute A100 1.",
            ),
        )

    if "insufficient" in text or "balance" in text or "fund" in text:
        return ErrorGuide(
            "Wallet funding issue",
            "This action needs A0GI for gas or payment, but the wallet does not have enough.",
            (
                "Run /connect to view your wallet address.",
                "Fund that address with A0GI on 0G mainnet.",
                "Run /balance before retrying the transaction.",
            ),
        )

    if "storage" in text or "indexer" in text:
        return ErrorGuide(
            "0G Storage issue",
            "The storage indexer could not complete the upload or lookup.",
            (
                "Retry with a smaller file.",
                "Run /stack to confirm the configured storage indexer.",
                "Keep the file and retry /store when the indexer is reachable.",
            ),
        )

    if "compute" in text or "0g-compute" in text or "provider" in text:
        return ErrorGuide(
            "0G Compute issue",
            "The compute provider discovery or purchase flow could not complete.",
            (
                "Run /compute_market to refresh providers.",
                "Run /compute_account to check compute CLI status.",
                "Retry the purchase after confirming /balance has enough A0GI.",
            ),
        )

    return ErrorGuide(
        "Unexpected bot error",
        "The command failed unexpectedly, but ZeroBot is still running.",
        (
            "Retry the command once.",
            "Run /commands to confirm the right command format.",
            "If it repeats, share the support code with the maintainer.",
        ),
    )


def format_error_message(error: BaseException, hint: str | None = None) -> str:
    guide = classify_error(error)
    code = support_code(error)
    lines = [
        f"<b>{html.escape(guide.title)}</b>",
        html.escape(guide.explanation),
        "",
        "<b>What to do next</b>",
    ]
    lines.extend(f"- {html.escape(step)}" for step in guide.next_steps)
    if hint:
        lines.extend(["", f"<b>Hint:</b> {html.escape(hint)}"])
    lines.extend(["", f"<b>Support code:</b> <code>{code}</code>"])
    return "\n".join(lines)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error = context.error or RuntimeError("Unknown error")
    code = support_code(error)
    logger.error(
        "Unhandled update error support_code=%s update=%r\n%s",
        code,
        update,
        "".join(traceback.format_exception(type(error), error, error.__traceback__)),
    )

    if not isinstance(update, Update):
        return
    target = update.effective_message
    try:
        if target:
            await target.reply_text(format_error_message(error), parse_mode="HTML")
        elif update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(format_error_message(error), parse_mode="HTML")
    except Exception:
        logger.exception("Failed to send user-facing error message support_code=%s", code)
