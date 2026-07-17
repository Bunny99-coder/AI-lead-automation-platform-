from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    direction: str
    channel: str
    subject: str | None
    body: str
    status: str
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel: str
    status: str
    messages: list[MessageResponse] = []
    created_at: datetime


class AIActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action_type: str
    tool_used: str | None
    success: bool
    error: str | None
    created_at: datetime


class AutomationEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    source: str
    status: str
    error: str | None
    retry_count: int
    created_at: datetime


class DashboardStats(BaseModel):
    total_leads: int
    qualified_leads: int
    unqualified_leads: int
    appointments: int
    active_follow_ups: int
    failed_automations: int
