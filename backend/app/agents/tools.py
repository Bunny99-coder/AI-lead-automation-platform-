from typing import Any

from pydantic import BaseModel, Field


class ToolGetLeadArgs(BaseModel):
    lead_id: int


class ToolUpdateLeadArgs(BaseModel):
    lead_id: int
    qualification_status: str | None = None
    pipeline_stage: str | None = None
    status: str | None = None


class ToolAddNoteArgs(BaseModel):
    lead_id: int
    note: str = Field(..., min_length=1, max_length=5000)


class ToolChangePipelineArgs(BaseModel):
    lead_id: int
    stage: str = Field(..., min_length=1, max_length=128)


class ToolAddTagArgs(BaseModel):
    lead_id: int
    tag: str = Field(..., min_length=1, max_length=64)


class ToolCreateFollowUpArgs(BaseModel):
    lead_id: int
    delay_hours: int = Field(default=24, ge=1, le=168)
    message: str | None = None


class ToolGetAvailabilityArgs(BaseModel):
    lead_id: int


class ToolBookAppointmentArgs(BaseModel):
    lead_id: int
    slot_id: str


class ToolSendMessageArgs(BaseModel):
    lead_id: int
    message: str = Field(..., min_length=1, max_length=2000)
    channel: str = Field(default="sms", pattern="^(sms|email)$")


TOOL_SCHEMAS: dict[str, type[BaseModel]] = {
    "get_lead": ToolGetLeadArgs,
    "update_lead": ToolUpdateLeadArgs,
    "add_lead_note": ToolAddNoteArgs,
    "change_pipeline_stage": ToolChangePipelineArgs,
    "add_tag": ToolAddTagArgs,
    "create_follow_up": ToolCreateFollowUpArgs,
    "get_available_appointments": ToolGetAvailabilityArgs,
    "book_appointment": ToolBookAppointmentArgs,
    "send_message": ToolSendMessageArgs,
}


def validate_tool_args(tool_name: str, args: dict[str, Any]) -> BaseModel:
    schema = TOOL_SCHEMAS.get(tool_name)
    if not schema:
        raise ValueError(f"Unknown tool: {tool_name}")
    return schema.model_validate(args)
