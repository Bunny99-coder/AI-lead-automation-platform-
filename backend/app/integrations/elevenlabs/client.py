import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.integrations.elevenlabs.base import ElevenLabsProvider

logger = logging.getLogger(__name__)


class MockElevenLabsProvider(ElevenLabsProvider):
    async def get_agent_config(self, agent_id: str) -> dict[str, Any]:
        return {"agent_id": agent_id, "mode": "mock", "tools": ["get-lead", "book-appointment"]}

    async def register_tool_webhook(self, tool_name: str, url: str) -> dict[str, Any]:
        logger.info("Mock ElevenLabs registered tool %s -> %s", tool_name, url)
        return {"tool": tool_name, "url": url, "status": "registered"}


class ElevenLabsClient(ElevenLabsProvider):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def get_agent_config(self, agent_id: str) -> dict[str, Any]:
        raise NotImplementedError("Real ElevenLabs client requires API credentials")

    async def register_tool_webhook(self, tool_name: str, url: str) -> dict[str, Any]:
        raise NotImplementedError("Real ElevenLabs client requires API credentials")


def get_elevenlabs_provider(settings: Settings | None = None) -> ElevenLabsProvider:
    settings = settings or get_settings()
    if settings.elevenlabs_use_mock or not settings.elevenlabs_api_key:
        return MockElevenLabsProvider()
    return ElevenLabsClient(settings)
