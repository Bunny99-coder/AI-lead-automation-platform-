from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.admin import DashboardStats
from app.services.automation_service import AutomationService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db_session)) -> DashboardStats:
    return AutomationService(db).get_dashboard_stats()


@router.get("/actions")
def recent_actions(limit: int = 20, db: Session = Depends(get_db_session)) -> dict:
    actions = AutomationService(db).get_recent_actions(limit)
    return {
        "items": [
            {
                "id": a.id,
                "lead_id": a.lead_id,
                "action_type": a.action_type,
                "tool_used": a.tool_used,
                "success": a.success,
                "created_at": a.created_at.isoformat(),
            }
            for a in actions
        ]
    }


@router.get("/webhooks")
def recent_webhooks(limit: int = 20, db: Session = Depends(get_db_session)) -> dict:
    events = AutomationService(db).get_recent_webhooks(limit)
    return {
        "items": [
            {
                "id": e.id,
                "source": e.source,
                "event_type": e.event_type,
                "status": e.status.value,
                "lead_id": e.lead_id,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ]
    }
