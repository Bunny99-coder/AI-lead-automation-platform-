from sqlalchemy.orm import Session

from app.models.webhook_event import WebhookEvent


def is_duplicate_webhook(db: Session, idempotency_key: str) -> bool:
    return (
        db.query(WebhookEvent)
        .filter(WebhookEvent.idempotency_key == idempotency_key)
        .first()
        is not None
    )
