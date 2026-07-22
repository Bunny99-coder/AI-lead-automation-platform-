import logging

from sqlalchemy.orm import Session

from app.models.ai_action import AIAction
from app.models.appointment import Appointment
from app.models.automation_event import AutomationEvent, AutomationEventStatus
from app.models.lead import Lead, LeadStatus, QualificationStatus
from app.models.webhook_event import WebhookEvent, WebhookEventStatus
from app.schemas.admin import DashboardStats

logger = logging.getLogger(__name__)


class AutomationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record_webhook(
        self,
        source: str,
        event_type: str,
        idempotency_key: str,
        payload: dict,
        correlation_id: str,
        lead_id: int | None = None,
        duplicate: bool = False,
    ) -> WebhookEvent:
        event = WebhookEvent(
            source=source,
            event_type=event_type,
            idempotency_key=idempotency_key,
            payload=payload,
            lead_id=lead_id,
            correlation_id=correlation_id,
            status=WebhookEventStatus.DUPLICATE if duplicate else WebhookEventStatus.RECEIVED,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def mark_webhook_processed(self, event: WebhookEvent, lead_id: int | None = None) -> None:
        event.status = WebhookEventStatus.PROCESSED
        if lead_id:
            event.lead_id = lead_id
        self.db.commit()

    def mark_webhook_failed(self, event: WebhookEvent, error: str) -> None:
        event.status = WebhookEventStatus.FAILED
        event.error = error
        self.db.commit()

    def create_automation_event(
        self, event_type: str, source: str, lead_id: int | None, payload: dict, correlation_id: str
    ) -> AutomationEvent:
        event = AutomationEvent(
            event_type=event_type,
            source=source,
            lead_id=lead_id,
            payload=payload,
            correlation_id=correlation_id,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_dashboard_stats(self) -> DashboardStats:
        total = self.db.query(Lead).count()
        qualified = self.db.query(Lead).filter(Lead.qualification_status == QualificationStatus.QUALIFIED).count()
        unqualified = self.db.query(Lead).filter(
            Lead.qualification_status == QualificationStatus.UNQUALIFIED
        ).count()
        appointments = self.db.query(Appointment).count()
        follow_ups = self.db.query(Lead).filter(Lead.status == LeadStatus.FOLLOW_UP).count()
        failed = self.db.query(AutomationEvent).filter(
            AutomationEvent.status.in_([AutomationEventStatus.FAILED, AutomationEventStatus.DEAD_LETTER])
        ).count()
        return DashboardStats(
            total_leads=total,
            qualified_leads=qualified,
            unqualified_leads=unqualified,
            appointments=appointments,
            active_follow_ups=follow_ups,
            failed_automations=failed,
        )

    def get_recent_actions(self, limit: int = 20) -> list[AIAction]:
        return self.db.query(AIAction).order_by(AIAction.created_at.desc()).limit(limit).all()

    def get_recent_webhooks(self, limit: int = 20) -> list[WebhookEvent]:
        return self.db.query(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(limit).all()

    def get_lead_events(self, lead_id: int) -> list[AutomationEvent]:
        return (
            self.db.query(AutomationEvent)
            .filter(AutomationEvent.lead_id == lead_id)
            .order_by(AutomationEvent.created_at.desc())
            .all()
        )

    def get_lead_actions(self, lead_id: int) -> list[AIAction]:
        return (
            self.db.query(AIAction)
            .filter(AIAction.lead_id == lead_id)
            .order_by(AIAction.created_at.desc())
            .all()
        )
