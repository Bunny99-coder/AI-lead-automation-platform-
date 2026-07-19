from abc import ABC, abstractmethod
from typing import Any


class ElevenLabsProvider(ABC):
    @abstractmethod
    async def get_agent_config(self, agent_id: str) -> dict[str, Any]: ...

    @abstractmethod
    async def register_tool_webhook(self, tool_name: str, url: str) -> dict[str, Any]: ...
