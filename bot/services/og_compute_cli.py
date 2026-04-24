"""Helpers for querying the 0G Compute CLI with a mainnet fallback config."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
from pathlib import Path

from bot.config import settings

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".0g-compute-cli"
CONFIG_PATH = CONFIG_DIR / "config.json"
NPX_FALLBACK = ["npx", "-y", "@0glabs/0g-serving-broker"]


def _command_prefix() -> list[str]:
    preferred = settings.og_compute_cli_bin.strip()
    if preferred and shutil.which(preferred):
        return [preferred]
    return NPX_FALLBACK


def _ensure_cli_config() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "rpcEndpoint": settings.og_compute_cli_rpc,
        "network": settings.og_compute_cli_network,
    }
    if CONFIG_PATH.exists():
        try:
            current = json.loads(CONFIG_PATH.read_text())
        except Exception:
            current = {}
        current.update(payload)
        payload = current
    CONFIG_PATH.write_text(json.dumps(payload, indent=2))


async def _run_cli(*args: str, timeout: int = 25) -> str:
    _ensure_cli_config()
    cmd = _command_prefix() + list(args)
    env = os.environ.copy()
    env.setdefault("HOME", str(Path.home()))
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        raise RuntimeError("0G Compute CLI request timed out")

    output = stdout.decode().strip()
    error = stderr.decode().strip()
    if process.returncode != 0:
        raise RuntimeError(error or output or "0G Compute CLI command failed")
    return output or error or "No output returned."


async def get_stack_summary() -> str:
    lines = [
        "0G mainnet stack used by ZeroBot",
        "",
        f"Chain RPC: {settings.og_rpc_url}",
        f"Chain ID: {settings.og_chain_id}",
        f"Explorer: {settings.og_explorer_url}",
        f"Storage Indexer: {settings.og_storage_indexer}",
        f"Compute CLI network: {settings.og_compute_cli_network}",
        "Compute CLI features: provider discovery, account status, model catalog",
    ]
    if settings.zerobot_contract_address:
        lines.append(f"ZeroBot contract: {settings.zerobot_contract_address}")
    return "\n".join(lines)


async def get_network_status() -> str:
    return await _run_cli("show-network")


async def get_account_status() -> str:
    return await _run_cli("get-account")


async def list_compute_providers() -> str:
    return await _run_cli("inference", "list-providers")


async def list_model_catalog() -> str:
    return await _run_cli("fine-tuning", "list-models")
