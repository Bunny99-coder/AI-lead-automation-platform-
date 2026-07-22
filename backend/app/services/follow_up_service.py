import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.integrations.messaging.providers import MockEmailProvider, MockSmsProvider
from app.models.automation_event import AutomationEvent, AutomationEventStatus
from app.models.lead import Lead, LeadStatus, QualificationStatus
from app.models.message import Message, MessageChannel, MessageDirection
from app.services.message_service import MessageService

logger = logging.getLogger(__name__)


class FollowUpService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.message_service = MessageService(db)
        self.sms = MockSmsProvider()
        self.email = MockEmailProvider()
        self.max_retries = 3

    async def schedule_follow_up(
        self, lead: Lead, delay_hours: int = 24, message: str | None = None, send_email: bool = False
    ) -> dict:
        event = AutomationEvent(
            event_type="follow_up_scheduled",
            source="system",
            lead_id=lead.id,
            payload={
                "delay_hours": delay_hours,
                "message": message,
                "send_email": send_email,
                "scheduled_for": (datetime.now(timezone.utc) + timedelta(hours=delay_hours)).isoformat(),
            },
            status=AutomationEventStatus.PENDING,
        )
        lead.status = LeadStatus.FOLLOW_UP
        self.db.add(event)
        self.db.commit()

        # For demo, execute immediately if delay is small or in tests
        if delay_hours <= 1:
            await self.execute_follow_up(event.id)

        return {"event_id": event.id, "lead_id": lead.id, "status": "scheduled"}

    async def execute_follow_up(self, event_id: int) -> None:
        event = self.db.query(AutomationEvent).filter(AutomationEvent.id == event_id).first()
        if not event or not event.lead_id:
            return

        lead = self.db.query(Lead).filter(Lead.id == event.lead_id).first()
        if not lead:
            event.status = AutomationEventStatus.FAILED
            event.error = "Lead not found"
            self.db.commit()
            return

        if lead.appointment_id:
            event.status = AutomationEventStatus.COMPLETED
            event.payload = {**(event.payload or {}), "skipped": "appointment_already_booked"}
            self.db.commit()
            return

        payload = event.payload or {}
        message = payload.get("message") or "Hi! Just following up — would you like to schedule a consultation?"

        try:
            if lead.phone:
                await self.sms.send_sms(lead.phone, message)
                await self.message_service.record_outbound(lead, message, MessageChannel.SMS)
            if payload.get("send_email") and lead.email:
                await self.email.send_email(lead.email, "Follow up", message)
                await self.message_service.record_outbound(
                    lead, message, MessageChannel.EMAIL, subject="Follow up"
                )
            event.status = AutomationEventStatus.COMPLETED
            self.db.commit()
        except Exception as exc:
            event.retry_count += 1
            event.error = str(exc)
            if event.retry_count >= self.max_retries:
                event.status = AutomationEventStatus.DEAD_LETTER
            else:
                event.status = AutomationEventStatus.FAILED
            self.db.commit()
            logger.exception("Follow-up failed for event %s", event_id)
            raise

    async def process_pending_follow_ups(self) -> int:
        events = (
            self.db.query(AutomationEvent)
            .filter(
                AutomationEvent.event_type == "follow_up_scheduled",
                AutomationEvent.status.in_([AutomationEventStatus.PENDING, AutomationEventStatus.FAILED]),
                AutomationEvent.retry_count < self.max_retries,
            )
            .all()
        )
        processed = 0
        for event in events:
            lead = self.db.query(Lead).filter(Lead.id == event.lead_id).first()
            if (
                lead
                and lead.qualification_status == QualificationStatus.QUALIFIED
                and not lead.appointment_id
            ):
                await self.execute_follow_up(event.id)
                processed += 1
        return processed
