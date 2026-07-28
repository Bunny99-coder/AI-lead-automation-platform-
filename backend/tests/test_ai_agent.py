import pytest

from app.agents.tools import validate_tool_args
from app.schemas.ai import LeadDecision, NextAction


def test_lead_decision_schema():
    decision = LeadDecision(
        intent="inquiry",
        qualification_status="unknown",
        confidence=0.7,
        next_action=NextAction.ASK_QUALIFICATION,
        reason="Initial contact",
        response="What service are you interested in?",
    )
    assert decision.confidence == 0.7


def test_tool_argument_validation():
    args = validate_tool_args("add_lead_note", {"lead_id": 1, "note": "Test note"})
    assert args.lead_id == 1


def test_invalid_tool_raises():
    with pytest.raises(ValueError):
        validate_tool_args("unknown_tool", {"lead_id": 1})


def test_book_appointment_requires_slot_id():
    with pytest.raises(Exception):
        validate_tool_args("book_appointment", {"lead_id": 1})
