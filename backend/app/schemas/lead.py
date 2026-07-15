from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadStatusSchema(str, Enum):
    new = "new"
    contacted = "contacted"
    qualifying = "qualifying"
    qualified = "qualified"
    unqualified = "unqualified"
    appointment_booked = "appointment_booked"
    follow_up = "follow_up"
    closed = "closed"
    error = "error"


class QualificationStatusSchema(str, Enum):
    unknown = "unknown"
    qualified = "qualified"
    unqualified = "unqualified"
    needs_review = "needs_review"


class LeadBase(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    pipeline_stage: str | None = None


class LeadCreate(LeadBase):
    ghl_contact_id: str


class LeadUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    status: LeadStatusSchema | None = None
    qualification_status: QualificationStatusSchema | None = None
    pipeline_stage: str | None = None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ghl_contact_id: str
    name: str | None
    email: str | None
    phone: str | None
    status: LeadStatusSchema
    qualification_status: QualificationStatusSchema
    pipeline_stage: str | None
    appointment_id: int | None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
