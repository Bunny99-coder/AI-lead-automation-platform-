import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from app.integrations.ghl.base import GHLProvider

logger = logging.getLogger(__name__)


class MockGHLProvider(GHLProvider):
    """In-memory mock GHL provider for local development and tests."""

    def __init__(self) -> None:
        self.contacts: dict[str, dict[str, Any]] = {}
        self.notes: dict[str, list[str]] = {}
        self.tags: dict[str, list[str]] = {}
        self.pipeline_stages: dict[str, str] = {}
        self.tasks: dict[str, list[dict[str, Any]]] = {}
        self.appointments: dict[str, list[dict[str, Any]]] = {}
        self._slots = self._generate_default_slots()

    def _generate_default_slots(self) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        slots = []
        for day in range(1, 8):
            for hour in (10, 14, 16):
                start = now + timedelta(days=day, hours=hour - now.hour if day == 1 else hour)
                start = start.replace(hour=hour)
                end = start + timedelta(minutes=30)
                slots.append(
                    {
                        "slot_id": f"slot-{uuid4().hex[:8]}",
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                    }
                )
        return slots

    async def get_contact(self, contact_id: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        if contact_id not in self.contacts:
            self.contacts[contact_id] = {
                "id": contact_id,
                "firstName": "New",
                "lastName": "Lead",
                "email": f"{contact_id}@example.com",
                "phone": "+15550001111",
            }
        return self.contacts[contact_id]

    async def update_contact(self, contact_id: str, data: dict[str, Any]) -> dict[str, Any]:
        await asyncio.sleep(0)
        contact = await self.get_contact(contact_id)
        contact.update(data)
        self.contacts[contact_id] = contact
        return contact

    async def add_note(self, contact_id: str, body: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        self.notes.setdefault(contact_id, []).append(body)
        return {"contact_id": contact_id, "note": body}

    async def add_tag(self, contact_id: str, tag: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        tags = self.tags.setdefault(contact_id, [])
        if tag not in tags:
            tags.append(tag)
        return {"contact_id": contact_id, "tags": tags}

    async def update_pipeline_stage(self, contact_id: str, stage: str) -> dict[str, Any]:
        await asyncio.sleep(0)
        self.pipeline_stages[contact_id] = stage
        return {"contact_id": contact_id, "stage": stage}

    async def create_task(
        self, contact_id: str, title: str, due_date: datetime | None = None
    ) -> dict[str, Any]:
        await asyncio.sleep(0)
        task = {"id": uuid4().hex, "title": title, "due_date": due_date.isoformat() if due_date else None}
        self.tasks.setdefault(contact_id, []).append(task)
        return task

    async def get_calendar_availability(
        self, calendar_id: str, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        await asyncio.sleep(0)
        result = []
        for slot in self._slots:
            slot_start = datetime.fromisoformat(slot["start"])
            if start <= slot_start <= end:
                result.append(slot)
        return result

    async def create_appointment(
        self,
        contact_id: str,
        calendar_id: str,
        slot_start: datetime,
        slot_end: datetime,
        notes: str | None = None,
    ) -> dict[str, Any]:
        await asyncio.sleep(0)
        appt_id = f"ghl-appt-{uuid4().hex[:8]}"
        appt = {
            "id": appt_id,
            "contact_id": contact_id,
            "calendar_id": calendar_id,
            "start": slot_start.isoformat(),
            "end": slot_end.isoformat(),
            "notes": notes,
        }
        self.appointments.setdefault(contact_id, []).append(appt)
        self._slots = [s for s in self._slots if s["start"] != slot_start.isoformat()]
        return appt

    def set_fail_next(self, count: int = 1) -> None:
        self._fail_remaining = count  # type: ignore[attr-defined]
