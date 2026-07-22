from sqlalchemy.orm import Session

from app.integrations.messaging.providers import MockEmailProvider, MockSmsProvider
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.models.message import Message, MessageChannel, MessageDirection


class MessageService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sms = MockSmsProvider()
        self.email = MockEmailProvider()

    def get_conversation_history(self, lead_id: int) -> list[dict[str, str]]:
        messages = (
            self.db.query(Message)
            .filter(Message.lead_id == lead_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        history = []
        for msg in messages:
            role = "user" if msg.direction == MessageDirection.INBOUND else "assistant"
            history.append({"role": role, "content": msg.body})
        return history

    def get_conversations(self, lead_id: int) -> list[Conversation]:
        return self.db.query(Conversation).filter(Conversation.lead_id == lead_id).all()

    async def send_to_lead(self, lead: Lead, message: str, channel: str = "sms") -> dict:
        if channel == "email":
            if not lead.email:
                raise ValueError("Lead has no email")
            result = await self.email.send_email(lead.email, "Message from our team", message)
            await self.record_outbound(lead, message, MessageChannel.EMAIL, subject="Message from our team")
            return result
        if not lead.phone:
            raise ValueError("Lead has no phone")
        result = await self.sms.send_sms(lead.phone, message)
        await self.record_outbound(lead, message, MessageChannel.SMS)
        return result

    async def record_outbound(
        self, lead: Lead, body: str, channel: MessageChannel, subject: str | None = None
    ) -> Message:
        conv = (
            self.db.query(Conversation)
            .filter(Conversation.lead_id == lead.id)
            .first()
        )
        if not conv:
            conv = Conversation(lead_id=lead.id, channel=channel.value)
            self.db.add(conv)
            self.db.flush()
        msg = Message(
            lead_id=lead.id,
            conversation_id=conv.id,
            direction=MessageDirection.OUTBOUND,
            channel=channel,
            subject=subject,
            body=body,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg
