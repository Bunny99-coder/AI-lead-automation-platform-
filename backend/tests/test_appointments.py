import pytest
from unittest.mock import patch

from app.integrations.ghl.mock import MockGHLProvider
from app.models.lead import Lead, LeadStatus
from app.services.appointment_service import AppointmentService
from app.services.lead_service import LeadService


@pytest.fixture
def lead(db_session):
    lead = Lead(
        ghl_contact_id="contact-test-001",
        name="Test Lead",
        email="test@example.com",
        phone="+15550009999",
        status=LeadStatus.NEW,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.mark.asyncio
async def test_appointment_scheduling(db_session, lead):
    with patch("app.services.appointment_service.get_ghl_provider", return_value=MockGHLProvider()):
        service = AppointmentService(db_session)
        slots = await service.get_availability()
        assert len(slots) > 0
        result = await service.book_appointment(lead, slots[0].slot_id)
        assert result["appointment_id"] is not None


@pytest.mark.asyncio
async def test_invalid_appointment_slot(db_session, lead):
    with patch("app.services.appointment_service.get_ghl_provider", return_value=MockGHLProvider()):
        service = AppointmentService(db_session)
        with pytest.raises(Exception):
            await service.book_appointment(lead, "invalid-slot-id")


@pytest.mark.asyncio
async def test_pipeline_update(db_session, lead):
    with patch("app.services.lead_service.get_ghl_provider", return_value=MockGHLProvider()):
        service = LeadService(db_session)
        result = await service.change_pipeline(lead, "Qualified")
        assert result["pipeline_stage"] == "Qualified"
