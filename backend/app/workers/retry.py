import asyncio
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def retry_with_backoff(coro_factory, max_retries: int | None = None):
    settings = get_settings()
    retries = max_retries or settings.max_retries
    delay = settings.retry_base_delay_seconds
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return await coro_factory()
        except Exception as exc:
            last_exc = exc
            logger.warning("Retry attempt %s failed: %s", attempt, exc)
            if attempt < retries:
                await asyncio.sleep(delay)
                delay *= 2
    raise last_exc or RuntimeError("Retry failed")
