from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class GHLProvider(ABC):
    @abstractmethod
    async def get_contact(self, contact_id: str) -> dict[str, Any]: ...

    @abstractmethod
    async def update_contact(self, contact_id: str, data: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    async def add_note(self, contact_id: str, body: str) -> dict[str, Any]: ...

    @abstractmethod
    async def add_tag(self, contact_id: str, tag: str) -> dict[str, Any]: ...

    @abstractmethod
    async def update_pipeline_stage(self, contact_id: str, stage: str) -> dict[str, Any]: ...

    @abstractmethod
    async def create_task(self, contact_id: str, title: str, due_date: datetime | None = None) -> dict[str, Any]: ...

    @abstractmethod
    async def get_calendar_availability(
        self, calendar_id: str, start: datetime, end: datetime
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def create_appointment(
        self, contact_id: str, calendar_id: str, slot_start: datetime, slot_end: datetime, notes: str | None = None
    ) -> dict[str, Any]: ...
