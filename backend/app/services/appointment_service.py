from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.integrations.ghl.client import get_ghl_provider
from app.models.appointment import Appointment, AppointmentStatus
from app.models.lead import Lead, LeadStatus
from app.models.lead import QualificationStatus
from app.schemas.appointment import AppointmentSlot


class AppointmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.ghl = get_ghl_provider(self.settings)
        self._slot_cache: dict[str, AppointmentSlot] = {}

    async def get_availability(self, days: int = 7) -> list[AppointmentSlot]:
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=days)
        raw = await self.ghl.get_calendar_availability(self.settings.ghl_calendar_id or "default", start, end)
        slots: list[AppointmentSlot] = []
        self._slot_cache.clear()
        for item in raw:
            slot = AppointmentSlot(
                slot_id=item["slot_id"],
                start=datetime.fromisoformat(item["start"]),
                end=datetime.fromisoformat(item["end"]),
            )
            slots.append(slot)
            self._slot_cache[slot.slot_id] = slot
        return slots

    async def get_availability_for_lead(self, lead: Lead) -> dict:
        slots = await self.get_availability()
        return {
            "lead_id": lead.id,
            "slots": [s.model_dump(mode="json") for s in slots],
        }

    async def book_appointment(self, lead: Lead, slot_id: str) -> dict:
        if slot_id not in self._slot_cache:
            await self.get_availability()
        slot = self._slot_cache.get(slot_id)
        if not slot:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid appointment slot")

        ghl_appt = await self.ghl.create_appointment(
            lead.ghl_contact_id,
            self.settings.ghl_calendar_id or "default",
            slot.start,
            slot.end,
            notes=f"Booked via AI for lead {lead.id}",
        )
        appointment = Appointment(
            lead_id=lead.id,
            ghl_appointment_id=ghl_appt.get("id"),
            slot_start=slot.start,
            slot_end=slot.end,
            status=AppointmentStatus.CONFIRMED,
            notes="AI booked appointment",
        )
        self.db.add(appointment)
        self.db.flush()
        lead.appointment_id = appointment.id
        lead.status = LeadStatus.APPOINTMENT_BOOKED
        lead.qualification_status = QualificationStatus.QUALIFIED
        lead.pipeline_stage = lead.pipeline_stage or "Appointment Booked"
        self.db.commit()
        await self.ghl.add_note(lead.ghl_contact_id, f"Appointment booked for {slot.start.isoformat()}")
        await self.ghl.update_pipeline_stage(lead.ghl_contact_id, "Appointment Booked")
        return {"appointment_id": appointment.id, "ghl_appointment_id": appointment.ghl_appointment_id}
