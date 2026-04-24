"""0G compute marketplace service.

Since the 0G compute marketplace contract ABI isn't publicly standardized
yet, compute purchases are implemented as native OG token transfers to a
configurable compute provider address (OG_COMPUTE_PROVIDER_ADDRESS).

This performs REAL on-chain transactions. No simulation, no mocks.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from bot.services import wallet_service
from bot.config import settings
from bot.services.chain_service import (
    get_transaction_receipt,
    send_contract_transaction,
    send_native,
)

logger = logging.getLogger(__name__)

ZEROBOT_CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "gpu", "type": "string"},
            {"internalType": "uint256", "name": "durationHours", "type": "uint256"},
            {"internalType": "string", "name": "providerTag", "type": "string"},
        ],
        "name": "purchaseCompute",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "rootHash", "type": "string"},
            {"internalType": "string", "name": "fileName", "type": "string"},
        ],
        "name": "anchorStorage",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

# GPU pricing (OG per hour). Update these when 0G publishes compute prices.
GPU_PRICES = {
    "A100": 0.5,
    "H100": 1.2,
    "V100": 0.25,
    "T4": 0.1,
    "CPU": 0.05,
}


def _provider_address() -> str:
    """Return configured compute provider address, or empty string."""
    return os.environ.get("OG_COMPUTE_PROVIDER_ADDRESS", "").strip()


def _contract_address() -> str:
    return settings.zerobot_contract_address.strip()


def _compute_cost(gpu_type: str, duration_hours: int) -> float:
    """Calculate cost in OG for the given GPU and duration."""
    rate = GPU_PRICES.get(gpu_type.upper(), GPU_PRICES["A100"])
    return round(rate * duration_hours, 6)


@dataclass
class ComputeJob:
    job_id: str
    status: str  # "pending" | "submitted" | "confirmed" | "failed"
    gpu_type: str
    duration_hours: int
    cost_og: float
    tx_hash: str = ""


async def buy_compute(
    telegram_id: int,
    gpu_type: str = "A100",
    duration_hours: int = 1,
) -> ComputeJob:
    """Prepare a pending compute purchase for user confirmation.

    Does NOT execute the transaction yet - returns a pending job
    that the user confirms via the inline keyboard.
    """
    gpu_type = gpu_type.upper()
    if gpu_type not in GPU_PRICES:
        raise ValueError(
            f"Unknown GPU type: {gpu_type}. Choose from {list(GPU_PRICES.keys())}"
        )
    if duration_hours <= 0 or duration_hours > 720:
        raise ValueError("Duration must be 1-720 hours.")

    cost = _compute_cost(gpu_type, duration_hours)
    job_id = f"job_{telegram_id}_{int(time.time())}"

    logger.info(
        "Pending compute job created: user=%s gpu=%s hours=%s cost=%s OG",
        telegram_id, gpu_type, duration_hours, cost,
    )
    return ComputeJob(
        job_id=job_id,
        status="pending",
        gpu_type=gpu_type,
        duration_hours=duration_hours,
        cost_og=cost,
    )


async def confirm_compute_purchase(
    telegram_id: int,
    job_id: str,
    gpu_type: str,
    duration_hours: int,
) -> ComputeJob:
    """Execute a REAL on-chain transaction for the compute purchase."""
    cost = _compute_cost(gpu_type, duration_hours)
    provider = _provider_address()
    contract_address = _contract_address()

    if (
        not contract_address
        and (not provider or provider == "0x0000000000000000000000000000000000000000")
    ):
        logger.warning("OG_COMPUTE_PROVIDER_ADDRESS not configured - cannot execute")
        return ComputeJob(
            job_id=job_id,
            status="failed",
            gpu_type=gpu_type,
            duration_hours=duration_hours,
            cost_og=cost,
        )

    try:
        user = await wallet_service.get_user(telegram_id)
        if user is None:
            raise RuntimeError("User has no wallet")

        private_key = await wallet_service.get_private_key(telegram_id)
        if not private_key:
            raise RuntimeError("Wallet not found")

        if contract_address:
            tx_hash = await send_contract_transaction(
                private_key=private_key,
                from_address=user.wallet_address or "",
                contract_address=contract_address,
                abi=ZEROBOT_CONTRACT_ABI,
                function_name="purchaseCompute",
                args=[gpu_type, duration_hours, settings.og_compute_provider_tag],
                value_og=cost,
            )
        else:
            tx_hash = await send_native(
                private_key=private_key,
                from_address=user.wallet_address or "",
                to_address=provider,
                amount_og=cost,
            )

        logger.info(
            "Compute purchase broadcast: user=%s job=%s tx=%s",
            telegram_id, job_id, tx_hash,
        )
        return ComputeJob(
            job_id=job_id,
            status="submitted",
            gpu_type=gpu_type,
            duration_hours=duration_hours,
            cost_og=cost,
            tx_hash=tx_hash,
        )
    except Exception as e:
        logger.exception("Compute purchase failed: %s", e)
        return ComputeJob(
            job_id=job_id,
            status="failed",
            gpu_type=gpu_type,
            duration_hours=duration_hours,
            cost_og=cost,
        )


async def get_job_status(job_id: str, tx_hash: str = "") -> Optional[ComputeJob]:
    """Check the on-chain status of a compute job by its tx hash."""
    if not tx_hash:
        return None
    try:
        receipt = get_transaction_receipt(tx_hash)
        if receipt is None:
            status = "pending"
        else:
            status = "confirmed" if receipt.get("status") == 1 else "failed"
        return ComputeJob(
            job_id=job_id,
            status=status,
            gpu_type="",
            duration_hours=0,
            cost_og=0.0,
            tx_hash=tx_hash,
        )
    except Exception as e:
        logger.error("Status check failed: %s", e)
        return None
