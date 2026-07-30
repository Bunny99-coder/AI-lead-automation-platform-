import pytest
from unittest.mock import patch

from app.models.lead import Lead, LeadStatus, QualificationStatus
from app.services.follow_up_service import FollowUpService


@pytest.fixture
def qualified_lead(db_session):
    lead = Lead(
        ghl_contact_id="contact-followup-001",
        name="Follow Up Lead",
        email="followup@example.com",
        phone="+15550008888",
        status=LeadStatus.QUALIFIED,
        qualification_status=QualificationStatus.QUALIFIED,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.mark.asyncio
async def test_follow_up_scheduling(db_session, qualified_lead):
    service = FollowUpService(db_session)
    result = await service.schedule_follow_up(qualified_lead, delay_hours=1, message="Follow up message")
    assert result["event_id"] is not None
