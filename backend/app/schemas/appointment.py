from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AppointmentSlot(BaseModel):
    start: datetime
    end: datetime
    slot_id: str


class AvailabilityResponse(BaseModel):
    slots: list[AppointmentSlot]


class BookAppointmentRequest(BaseModel):
    slot_id: str
    notes: str | None = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    ghl_appointment_id: str | None
    slot_start: datetime
    slot_end: datetime
    status: str
    notes: str | None
    created_at: datetime


class AppointmentCreate(BaseModel):
    lead_id: int
    slot_id: str = Field(..., description="Must match a slot from availability API")
    notes: str | None = None
