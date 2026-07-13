import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageChannel(str, enum.Enum):
    SMS = "sms"
    EMAIL = "email"
    VOICE = "voice"
    WEBHOOK = "webhook"
    SYSTEM = "system"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversations.id"), nullable=True)
    direction: Mapped[MessageDirection] = mapped_column(Enum(MessageDirection))
    channel: Mapped[MessageChannel] = mapped_column(Enum(MessageChannel))
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(64), default="sent")
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lead: Mapped["Lead"] = relationship(back_populates="messages")
    conversation: Mapped["Conversation | None"] = relationship(back_populates="messages")
