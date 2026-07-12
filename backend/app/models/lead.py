import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFYING = "qualifying"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    APPOINTMENT_BOOKED = "appointment_booked"
    FOLLOW_UP = "follow_up"
    CLOSED = "closed"
    ERROR = "error"


class QualificationStatus(str, enum.Enum):
    UNKNOWN = "unknown"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    NEEDS_REVIEW = "needs_review"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ghl_contact_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus), default=LeadStatus.NEW)
    qualification_status: Mapped[QualificationStatus] = mapped_column(
        Enum(QualificationStatus), default=QualificationStatus.UNKNOWN
    )
    pipeline_stage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    appointment_id: Mapped[int | None] = mapped_column(ForeignKey("appointments.id"), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="lead")
    messages: Mapped[list["Message"]] = relationship(back_populates="lead")
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="lead", foreign_keys="Appointment.lead_id"
    )
    automation_events: Mapped[list["AutomationEvent"]] = relationship(back_populates="lead")
    ai_actions: Mapped[list["AIAction"]] = relationship(back_populates="lead")
