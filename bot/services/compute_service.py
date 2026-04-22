"""0G compute marketplace interaction.

The 0G compute API is not yet publicly documented.  This module provides
the buy / confirm / status flow.  ``confirm_compute_purchase`` is where
the real on-chain transaction would be broadcast once the 0G compute
marketplace contract ABI is available.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ComputeJob:
    job_id: str
    status: str  # "pending" | "confirmed" | "running" | "completed" | "failed"
    gpu_type: str
    duration_hours: int
    cost_a0gi: float


async def buy_compute(
    telegram_id: int,
    gpu_type: str = "A100",
    duration_hours: int = 1,
) -> ComputeJob:
    """Create a *pending* compute purchase request.

    This does NOT execute a transaction -- it prepares the order for the
    user to confirm via the inline keyboard.
    """
    logger.info(
        "Compute purchase requested: user=%s gpu=%s hours=%s",
        telegram_id,
        gpu_type,
        duration_hours,
    )
    cost = duration_hours * 0.5
    job_id = f"job_{telegram_id}_{gpu_type}_{duration_hours}h"
    return ComputeJob(
        job_id=job_id,
        status="pending",
        gpu_type=gpu_type,
        duration_hours=duration_hours,
        cost_a0gi=cost,
    )


async def confirm_compute_purchase(
    telegram_id: int,
    job_id: str,
) -> ComputeJob:
    """Execute the confirmed compute purchase.

    When the 0G compute marketplace smart contract is publicly available
    this function will build, sign, and broadcast the real on-chain
    transaction using the user's wallet.  Until then we mark the job as
    confirmed so no simulated/fake tx hash is ever returned.
    """
    logger.info("Confirming compute purchase: user=%s job=%s", telegram_id, job_id)

    # TODO: Replace with real on-chain transaction once the 0G compute
    # marketplace contract ABI is published.  The flow will be:
    #   1. Load user private key via wallet_service.get_private_key()
    #   2. Build the contract call (marketplace.buy_compute(...))
    #   3. Sign and broadcast via chain_service.send_raw_transaction()
    #   4. Wait for receipt and return real tx hash

    return ComputeJob(
        job_id=job_id,
        status="confirmed",
        gpu_type="A100",
        duration_hours=1,
        cost_a0gi=0.5,
    )


async def get_job_status(job_id: str) -> Optional[ComputeJob]:
    """Query the status of a compute job."""
    logger.info("Job status query: %s", job_id)
    # TODO: Look up real job state from the 0G compute marketplace
    return ComputeJob(
        job_id=job_id,
        status="pending",
        gpu_type="A100",
        duration_hours=1,
        cost_a0gi=0.5,
    )
