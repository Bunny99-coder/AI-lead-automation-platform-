from pydantic import BaseModel, Field


class GHLContactPayload(BaseModel):
    id: str = Field(..., description="GoHighLevel contact ID")
    firstName: str | None = None
    lastName: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    tags: list[str] | None = None


class GHLWebhookPayload(BaseModel):
    type: str = Field(..., description="Event type from GHL")
    locationId: str | None = None
    id: str | None = Field(None, description="Event ID for idempotency")
    contact: GHLContactPayload
    message: str | None = None
    pipelineStage: str | None = None
    stage: str | None = None


class WebhookAcceptedResponse(BaseModel):
    status: str
    correlation_id: str
    lead_id: int | None = None
    duplicate: bool = False
