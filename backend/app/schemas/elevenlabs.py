from pydantic import BaseModel, Field


class ElevenLabsPostCallWebhook(BaseModel):
    call_id: str
    contact_id: str | None = None
    lead_id: int | None = None
    transcript: str | None = None
    summary: str | None = None
    call_outcome: str | None = None
    qualification_result: str | None = None
    appointment_info: dict | None = None


class ElevenLabsToolGetLeadRequest(BaseModel):
    contact_id: str | None = None
    lead_id: int | None = None


class ElevenLabsToolUpdateLeadRequest(BaseModel):
    lead_id: int
    qualification_status: str | None = None
    pipeline_stage: str | None = None
    note: str | None = None


class ElevenLabsToolBookAppointmentRequest(BaseModel):
    lead_id: int
    slot_id: str
    notes: str | None = None


class ElevenLabsToolAddNoteRequest(BaseModel):
    lead_id: int
    note: str
