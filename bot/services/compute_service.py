"""0G compute marketplace interaction.

The 0G compute API is not yet publicly documented, so this module provides
stub implementations that will be replaced once endpoints are finalised.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ComputeJob:
    job_id: str
    status: str  # "pending" | "running" | "completed" | "failed"
    gpu_type: str
    duration_hours: int
    cost_a0gi: float


async def buy_compute(
    telegram_id: int,
    gpu_type: str = "A100",
    duration_hours: int = 1,
) -> ComputeJob:
    """Submit a compute purchase request (stub).

    In production this will interact with the 0G compute marketplace
    smart contract or REST API.
    """
    logger.info(
        "Compute purchase requested: user=%s gpu=%s hours=%s",
        telegram_id,
        gpu_type,
        duration_hours,
    )
    # Placeholder -- return a mock job
    return ComputeJob(
        job_id="job_placeholder_001",
        status="pending",
        gpu_type=gpu_type,
        duration_hours=duration_hours,
        cost_a0gi=duration_hours * 0.5,
    )


async def get_job_status(job_id: str) -> Optional[ComputeJob]:
    """Query the status of a compute job (stub)."""
    logger.info("Job status query: %s", job_id)
    return ComputeJob(
        job_id=job_id,
        status="pending",
        gpu_type="A100",
        duration_hours=1,
        cost_a0gi=0.5,
    )
