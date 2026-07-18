import logging
from uuid import uuid4

from app.integrations.messaging.base import EmailProvider, SmsProvider

logger = logging.getLogger(__name__)


class MockSmsProvider(SmsProvider):
    sent: list[dict] = []

    async def send_sms(self, phone: str, message: str) -> dict:
        record = {"id": f"sms-{uuid4().hex[:8]}", "phone": phone, "message": message, "status": "sent"}
        self.sent.append(record)
        logger.info("Mock SMS sent to %s: %s", phone, message[:80])
        return record


class MockEmailProvider(EmailProvider):
    sent: list[dict] = []

    async def send_email(self, email: str, subject: str, body: str) -> dict:
        record = {
            "id": f"email-{uuid4().hex[:8]}",
            "email": email,
            "subject": subject,
            "body": body,
            "status": "sent",
        }
        self.sent.append(record)
        logger.info("Mock email sent to %s: %s", email, subject)
        return record
