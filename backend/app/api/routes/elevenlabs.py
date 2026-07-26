import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.lead_agent import LeadQualificationAgent
from app.api.deps import get_db_session
from app.core.security import verify_elevenlabs_secret
from app.models.message import Message, MessageChannel, MessageDirection
from app.schemas.elevenlabs import (
    ElevenLabsPostCallWebhook,
    ElevenLabsToolAddNoteRequest,
    ElevenLabsToolBookAppointmentRequest,
    ElevenLabsToolGetLeadRequest,
    ElevenLabsToolUpdateLeadRequest,
)
from app.services.appointment_service import AppointmentService
from app.services.automation_service import AutomationService
from app.services.lead_service import LeadService
from app.utils.correlation import set_correlation_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["elevenlabs"])


@router.post("/webhooks/elevenlabs")
async def elevenlabs_post_call_webhook(
    call_data: ElevenLabsPostCallWebhook,
    db: Session = Depends(get_db_session),
    _: None = Depends(verify_elevenlabs_secret),
) -> dict:
    correlation_id = set_correlation_id()
    automation = AutomationService(db)
    lead_service = LeadService(db)

    lead = None
    if call_data.lead_id:
        lead = lead_service.get_lead(call_data.lead_id)
    elif call_data.contact_id:
        lead = lead_service.get_lead_by_ghl_id(call_data.contact_id)

    automation.create_automation_event(
        event_type="elevenlabs_post_call",
        source="elevenlabs",
        lead_id=lead.id if lead else None,
        payload=call_data.model_dump(),
        correlation_id=correlation_id,
    )

    if lead and call_data.transcript:
        msg = Message(
            lead_id=lead.id,
            direction=MessageDirection.INBOUND,
            channel=MessageChannel.VOICE,
            body=call_data.transcript,
        )
        db.add(msg)
        db.commit()

    if lead and call_data.qualification_result:
        from app.models.lead import QualificationStatus

        try:
            lead.qualification_status = QualificationStatus(call_data.qualification_result)
            db.commit()
        except ValueError:
            logger.warning("Invalid qualification result: %s", call_data.qualification_result)

    if lead and call_data.summary:
        await lead_service.add_note(lead, f"Call summary: {call_data.summary}")

    return {"status": "processed", "correlation_id": correlation_id, "lead_id": lead.id if lead else None}


tools_router = APIRouter(prefix="/tools/elevenlabs", tags=["elevenlabs-tools"])


@tools_router.post("/get-lead")
async def elevenlabs_get_lead(
    request_data: ElevenLabsToolGetLeadRequest,
    db: Session = Depends(get_db_session),
    _: None = Depends(verify_elevenlabs_secret),
) -> dict:
    lead_service = LeadService(db)
    lead = None
    if request_data.lead_id:
        lead = lead_service.get_lead(request_data.lead_id)
    elif request_data.contact_id:
        lead = lead_service.get_lead_by_ghl_id(request_data.contact_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead_service.lead_to_dict(lead)


@tools_router.post("/update-lead")
async def elevenlabs_update_lead(
    request_data: ElevenLabsToolUpdateLeadRequest,
    db: Session = Depends(get_db_session),
    _: None = Depends(verify_elevenlabs_secret),
) -> dict:
    lead_service = LeadService(db)
    lead = lead_service.get_lead_or_raise(request_data.lead_id)
    if request_data.note:
        await lead_service.add_note(lead, request_data.note)
    return lead_service.update_lead_fields(
        lead,
        {
            "qualification_status": request_data.qualification_status,
            "pipeline_stage": request_data.pipeline_stage,
        },
    )


@tools_router.post("/book-appointment")
async def elevenlabs_book_appointment(
    request_data: ElevenLabsToolBookAppointmentRequest,
    db: Session = Depends(get_db_session),
    _: None = Depends(verify_elevenlabs_secret),
) -> dict:
    lead_service = LeadService(db)
    lead = lead_service.get_lead_or_raise(request_data.lead_id)
    service = AppointmentService(db)
    return await service.book_appointment(lead, request_data.slot_id)


@tools_router.post("/add-note")
async def elevenlabs_add_note(
    request_data: ElevenLabsToolAddNoteRequest,
    db: Session = Depends(get_db_session),
    _: None = Depends(verify_elevenlabs_secret),
) -> dict:
    lead_service = LeadService(db)
    lead = lead_service.get_lead_or_raise(request_data.lead_id)
    return await lead_service.add_note(lead, request_data.note)
