import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx

from app.core.config import Settings, get_settings
from app.integrations.ghl.base import GHLProvider

logger = logging.getLogger(__name__)


class GHLClient(GHLProvider):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.ghl_base_url.rstrip("/")
        self.timeout = self.settings.api_timeout_seconds
        self.max_retries = self.settings.max_retries

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.ghl_api_key}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        delay = self.settings.retry_base_delay_seconds
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, headers=self._headers(), **kwargs)
                    if response.status_code == 429:
                        logger.warning("GHL rate limit hit, retry %s", attempt)
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                    response.raise_for_status()
                    if response.content:
                        return response.json()
                    return {}
            except Exception as exc:
                last_error = exc
                logger.exception("GHL API error attempt=%s path=%s", attempt, path)
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2
        raise RuntimeError(f"GHL request failed after retries: {last_error}")

    async def get_contact(self, contact_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/contacts/{contact_id}")

    async def update_contact(self, contact_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PUT", f"/contacts/{contact_id}", json=data)

    async def add_note(self, contact_id: str, body: str) -> dict[str, Any]:
        return await self._request("POST", f"/contacts/{contact_id}/notes", json={"body": body})

    async def add_tag(self, contact_id: str, tag: str) -> dict[str, Any]:
        return await self._request("POST", f"/contacts/{contact_id}/tags", json={"tags": [tag]})

    async def update_pipeline_stage(self, contact_id: str, stage: str) -> dict[str, Any]:
        return await self._request(
            "PUT",
            f"/contacts/{contact_id}/pipeline",
            json={"stage": stage, "locationId": self.settings.ghl_location_id},
        )

    async def create_task(
        self, contact_id: str, title: str, due_date: datetime | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"title": title, "contactId": contact_id}
        if due_date:
            payload["dueDate"] = due_date.isoformat()
        return await self._request("POST", "/tasks/", json=payload)

    async def get_calendar_availability(
        self, calendar_id: str, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        data = await self._request(
            "GET",
            f"/calendars/{calendar_id}/free-slots",
            params={"startDate": start.isoformat(), "endDate": end.isoformat()},
        )
        return data.get("slots", [])

    async def create_appointment(
        self,
        contact_id: str,
        calendar_id: str,
        slot_start: datetime,
        slot_end: datetime,
        notes: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "calendarId": calendar_id,
            "contactId": contact_id,
            "startTime": slot_start.isoformat(),
            "endTime": slot_end.isoformat(),
            "notes": notes,
        }
        return await self._request("POST", "/calendars/events", json=payload)


def get_ghl_provider(settings: Settings | None = None) -> GHLProvider:
    settings = settings or get_settings()
    if settings.ghl_use_mock or not settings.ghl_api_key:
        from app.integrations.ghl.mock import MockGHLProvider

        return MockGHLProvider()
    return GHLClient(settings)
