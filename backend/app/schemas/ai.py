from enum import Enum

from pydantic import BaseModel, Field


class NextAction(str, Enum):
    SEND_MESSAGE = "send_message"
    ASK_QUALIFICATION = "ask_qualification"
    OFFER_APPOINTMENT = "offer_appointment"
    BOOK_APPOINTMENT = "book_appointment"
    SCHEDULE_FOLLOW_UP = "schedule_follow_up"
    ADD_NOTE = "add_note"
    UPDATE_PIPELINE = "update_pipeline"
    ESCALATE_HUMAN = "escalate_human"
    NO_ACTION = "no_action"


class LeadDecision(BaseModel):
    intent: str = Field(..., description="Detected lead intent")
    qualification_status: str = Field(..., description="qualified | unqualified | unknown | needs_review")
    confidence: float = Field(..., ge=0.0, le=1.0)
    next_action: NextAction
    reason: str
    response: str = Field(..., description="Message to send to the lead if applicable")
    requires_human: bool = False
    appointment_requested: bool = False
    preferred_slot_id: str | None = None
    tags_to_add: list[str] = Field(default_factory=list)
    pipeline_stage: str | None = None
    note: str | None = None
