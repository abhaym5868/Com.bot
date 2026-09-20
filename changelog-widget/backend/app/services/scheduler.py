"""
services/scheduler.py
---------------------
Background scheduler for auto-publishing SCHEDULED changelogs.

Architecture:
- Uses FastAPI's asyncio background task (no Celery/Redis required).
- A long-running coroutine checks every 60 seconds for SCHEDULED changelogs
  whose `scheduled_for` timestamp has passed and publishes them.
- Started in the app lifespan and cancelled on shutdown.
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.changelog_service import auto_publish_scheduled

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60  # Check every minute


async def scheduled_publisher_task(db: AsyncIOMotorDatabase) -> None:
    """
    Long-running background coroutine.
    Polls every CHECK_INTERVAL_SECONDS for SCHEDULED changelogs ready to publish.
    """
    logger.info("Scheduled publisher started (interval: %ds).", CHECK_INTERVAL_SECONDS)
    while True:
        try:
            count = await auto_publish_scheduled(db)
            if count > 0:
                logger.info("Scheduler auto-published %d changelog(s).", count)
        except asyncio.CancelledError:
            logger.info("Scheduled publisher cancelled — shutting down.")
            raise
        except Exception as exc:
            # Log but don't crash the scheduler
            logger.error("Scheduler error: %s", exc, exc_info=True)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
