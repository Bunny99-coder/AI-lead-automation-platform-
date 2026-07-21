import json
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.integrations.ghl.client import get_ghl_provider
from app.models.conversation import Conversation
from app.models.lead import Lead, LeadStatus, QualificationStatus
from app.models.message import Message, MessageChannel, MessageDirection
from app.schemas.webhook import GHLWebhookPayload

logger = logging.getLogger(__name__)


class LeadService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.ghl = get_ghl_provider(get_settings())

    def get_lead(self, lead_id: int) -> Lead | None:
        return self.db.query(Lead).filter(Lead.id == lead_id).first()

    def get_lead_or_raise(self, lead_id: int) -> Lead:
        lead = self.get_lead(lead_id)
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        return lead

    def get_lead_by_ghl_id(self, ghl_contact_id: str) -> Lead | None:
        return self.db.query(Lead).filter(Lead.ghl_contact_id == ghl_contact_id).first()

    def list_leads(self, skip: int = 0, limit: int = 50) -> tuple[list[Lead], int]:
        q = self.db.query(Lead).order_by(Lead.created_at.desc())
        total = q.count()
        return q.offset(skip).limit(limit).all(), total

    def upsert_from_webhook(self, payload: GHLWebhookPayload) -> Lead:
        if not payload.contact:
            raise ValueError("Webhook missing contact data")

        contact = payload.contact
        name = contact.name or " ".join(filter(None, [contact.firstName, contact.lastName])).strip() or None
        existing = self.get_lead_by_ghl_id(contact.id)

        if existing:
            existing.name = name or existing.name
            existing.email = contact.email or existing.email
            existing.phone = contact.phone or existing.phone
            existing.pipeline_stage = payload.pipelineStage or payload.stage or existing.pipeline_stage
            lead = existing
        else:
            lead = Lead(
                ghl_contact_id=contact.id,
                name=name,
                email=contact.email,
                phone=contact.phone,
                pipeline_stage=payload.pipelineStage or payload.stage,
                status=LeadStatus.NEW,
            )
            self.db.add(lead)
            self.db.flush()

        if payload.message:
            conv = (
                self.db.query(Conversation)
                .filter(Conversation.lead_id == lead.id, Conversation.channel == "sms")
                .first()
            )
            if not conv:
                conv = Conversation(lead_id=lead.id, channel="sms")
                self.db.add(conv)
                self.db.flush()
            msg = Message(
                lead_id=lead.id,
                conversation_id=conv.id,
                direction=MessageDirection.INBOUND,
                channel=MessageChannel.WEBHOOK,
                body=payload.message,
            )
            self.db.add(msg)

        self.db.commit()
        self.db.refresh(lead)
        return lead

    def update_qualification(self, lead: Lead, status: QualificationStatus) -> Lead:
        lead.qualification_status = status
        if status == QualificationStatus.QUALIFIED:
            lead.status = LeadStatus.QUALIFIED
        elif status == QualificationStatus.UNQUALIFIED:
            lead.status = LeadStatus.UNQUALIFIED
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def update_lead_fields(self, lead: Lead, data: dict) -> dict:
        if data.get("qualification_status"):
            lead.qualification_status = QualificationStatus(data["qualification_status"])
        if data.get("pipeline_stage"):
            lead.pipeline_stage = data["pipeline_stage"]
        if data.get("status"):
            lead.status = LeadStatus(data["status"])
        self.db.commit()
        return self.lead_to_dict(lead)

    async def add_note(self, lead: Lead, note: str) -> dict:
        await self.ghl.add_note(lead.ghl_contact_id, note)
        lead.notes = (lead.notes or "") + f"\n{note}"
        self.db.commit()
        return {"lead_id": lead.id, "note_added": True}

    async def change_pipeline(self, lead: Lead, stage: str) -> dict:
        await self.ghl.update_pipeline_stage(lead.ghl_contact_id, stage)
        lead.pipeline_stage = stage
        self.db.commit()
        return {"lead_id": lead.id, "pipeline_stage": stage}

    async def add_tag(self, lead: Lead, tag: str) -> dict:
        await self.ghl.add_tag(lead.ghl_contact_id, tag)
        tags = json.loads(lead.tags) if lead.tags else []
        if tag not in tags:
            tags.append(tag)
        lead.tags = json.dumps(tags)
        self.db.commit()
        return {"lead_id": lead.id, "tags": tags}

    def lead_to_dict(self, lead: Lead) -> dict:
        return {
            "id": lead.id,
            "ghl_contact_id": lead.ghl_contact_id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "status": lead.status.value,
            "qualification_status": lead.qualification_status.value,
            "pipeline_stage": lead.pipeline_stage,
            "appointment_id": lead.appointment_id,
        }
