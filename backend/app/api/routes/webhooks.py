import json
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.idempotency import is_duplicate_webhook
from app.core.security import hash_payload, verify_webhook_secret
from app.schemas.webhook import GHLWebhookPayload, WebhookAcceptedResponse
from app.services.automation_service import AutomationService
from app.services.lead_service import LeadService
from app.utils.correlation import set_correlation_id
from app.workers.processor import run_lead_processing_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/ghl", response_model=WebhookAcceptedResponse)
async def ghl_webhook(
    webhook_data: GHLWebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    _: None = Depends(verify_webhook_secret),
) -> WebhookAcceptedResponse:
    correlation_id = set_correlation_id()
    automation = AutomationService(db)

    idempotency_key = webhook_data.id or hash_payload(webhook_data.model_dump_json())
    if is_duplicate_webhook(db, idempotency_key):
        return WebhookAcceptedResponse(status="duplicate", correlation_id=correlation_id, duplicate=True)

    webhook_event = automation.record_webhook(
        source="ghl",
        event_type=webhook_data.type,
        idempotency_key=idempotency_key,
        payload=webhook_data.model_dump(),
        correlation_id=correlation_id,
    )

    try:
        lead_service = LeadService(db)
        lead = lead_service.upsert_from_webhook(webhook_data)
        automation.mark_webhook_processed(webhook_event, lead.id)

        background_tasks.add_task(run_lead_processing_task, lead.id, correlation_id)

        return WebhookAcceptedResponse(
            status="accepted",
            correlation_id=correlation_id,
            lead_id=lead.id,
        )
    except Exception as exc:
        logger.exception("GHL webhook processing failed")
        automation.mark_webhook_failed(webhook_event, str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
