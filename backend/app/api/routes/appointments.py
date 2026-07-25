from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.appointment import AvailabilityResponse
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(db: Session = Depends(get_db_session)) -> AvailabilityResponse:
    service = AppointmentService(db)
    slots = await service.get_availability()
    return AvailabilityResponse(slots=slots)
