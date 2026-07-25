from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.lead_agent import LeadQualificationAgent
from app.api.deps import get_db_session
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AvailabilityResponse, BookAppointmentRequest
from app.schemas.lead import LeadListResponse, LeadResponse
from app.services.appointment_service import AppointmentService
from app.services.lead_service import LeadService
from app.services.message_service import MessageService
from app.utils.correlation import set_correlation_id
from app.workers.processor import process_lead_async

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=LeadListResponse)
def list_leads(skip: int = 0, limit: int = 50, db: Session = Depends(get_db_session)) -> LeadListResponse:
    service = LeadService(db)
    items, total = service.list_leads(skip=skip, limit=limit)
    return LeadListResponse(items=items, total=total)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db_session)) -> LeadResponse:
    return LeadService(db).get_lead_or_raise(lead_id)


@router.get("/{lead_id}/conversation")
def get_conversation(lead_id: int, db: Session = Depends(get_db_session)) -> dict:
    LeadService(db).get_lead_or_raise(lead_id)
    history = MessageService(db).get_conversation_history(lead_id)
    return {"lead_id": lead_id, "messages": history}


@router.get("/{lead_id}/events")
def get_events(lead_id: int, db: Session = Depends(get_db_session)) -> dict:
    from app.services.automation_service import AutomationService

    LeadService(db).get_lead_or_raise(lead_id)
    events = AutomationService(db).get_lead_events(lead_id)
    return {
        "lead_id": lead_id,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "status": e.status.value,
                "error": e.error,
                "retry_count": e.retry_count,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
    }


@router.get("/{lead_id}/actions")
def get_actions(lead_id: int, db: Session = Depends(get_db_session)) -> dict:
    from app.services.automation_service import AutomationService

    LeadService(db).get_lead_or_raise(lead_id)
    actions = AutomationService(db).get_lead_actions(lead_id)
    return {
        "lead_id": lead_id,
        "actions": [
            {
                "id": a.id,
                "action_type": a.action_type,
                "tool_used": a.tool_used,
                "success": a.success,
                "error": a.error,
                "created_at": a.created_at.isoformat(),
            }
            for a in actions
        ],
    }


@router.post("/{lead_id}/process")
async def process_lead(lead_id: int, db: Session = Depends(get_db_session)) -> dict:
    LeadService(db).get_lead_or_raise(lead_id)
    correlation_id = set_correlation_id()
    await process_lead_async(db, lead_id, correlation_id)
    return {"status": "processed", "lead_id": lead_id, "correlation_id": correlation_id}


@router.post("/{lead_id}/qualify")
async def qualify_lead(lead_id: int, db: Session = Depends(get_db_session)) -> dict:
    LeadService(db).get_lead_or_raise(lead_id)
    agent = LeadQualificationAgent(db)
    decision = await agent.process_lead(lead_id)
    return decision.model_dump()


@router.post("/{lead_id}/appointment", response_model=AppointmentResponse)
async def book_lead_appointment(
    lead_id: int, body: BookAppointmentRequest, db: Session = Depends(get_db_session)
) -> Appointment:
    lead = LeadService(db).get_lead_or_raise(lead_id)
    result = await AppointmentService(db).book_appointment(lead, body.slot_id)
    appt = db.query(Appointment).filter(Appointment.id == result["appointment_id"]).first()
    if not appt:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Appointment not found")
    return appt
