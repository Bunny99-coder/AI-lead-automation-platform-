import asyncio
import logging

from sqlalchemy.orm import Session

from app.agents.lead_agent import LeadQualificationAgent
from app.models.automation_event import AutomationEvent, AutomationEventStatus
from app.services.automation_service import AutomationService
from app.services.follow_up_service import FollowUpService
from app.utils.correlation import set_correlation_id
from app.workers.retry import retry_with_backoff

logger = logging.getLogger(__name__)


async def process_lead_async(db: Session, lead_id: int, correlation_id: str) -> None:
    set_correlation_id(correlation_id)
    automation = AutomationService(db)
    event = automation.create_automation_event(
        event_type="lead_processing",
        source="worker",
        lead_id=lead_id,
        payload={"lead_id": lead_id},
        correlation_id=correlation_id,
    )
    event.status = AutomationEventStatus.PROCESSING
    db.commit()

    try:
        agent = LeadQualificationAgent(db)

        async def run():
            return await agent.process_lead(lead_id)

        decision = await retry_with_backoff(run)
        event.status = AutomationEventStatus.COMPLETED
        event.payload = {**(event.payload or {}), "decision": decision.model_dump()}
        db.commit()
        logger.info("Lead %s processed successfully", lead_id)
    except Exception as exc:
        logger.exception("Lead processing failed for %s", lead_id)
        event.retry_count += 1
        event.error = str(exc)
        settings_retries = 3
        if event.retry_count >= settings_retries:
            event.status = AutomationEventStatus.DEAD_LETTER
        else:
            event.status = AutomationEventStatus.FAILED
        db.commit()


async def run_lead_processing_task(lead_id: int, correlation_id: str) -> None:
    from app.db.session import get_session_factory

    db = get_session_factory()()
    try:
        await process_lead_async(db, lead_id, correlation_id)
    finally:
        db.close()


async def process_follow_ups(db: Session) -> int:
    service = FollowUpService(db)
    return await service.process_pending_follow_ups()
