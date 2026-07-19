import json
import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.schemas.ai import LeadDecision

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def qualify_lead(self, lead_context: dict[str, Any], conversation: list[dict[str, str]]) -> LeadDecision:
        if not self.settings.openai_api_key:
            return self._mock_decision(lead_context, conversation)

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            schema = LeadDecision.model_json_schema()
            prompt = (
                "You are a sales qualification agent. Analyze the lead and conversation. "
                "Never invent facts. Return structured JSON matching the schema. "
                f"Lead context: {json.dumps(lead_context)}\n"
                f"Conversation: {json.dumps(conversation)}"
            )
            response = await client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": "Return only valid JSON for lead qualification decisions."},
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": "lead_decision", "schema": schema},
                },
            )
            content = response.choices[0].message.content or "{}"
            return LeadDecision.model_validate_json(content)
        except Exception as exc:
            logger.warning("OpenAI unavailable, using mock decision: %s", exc)
            return self._mock_decision(lead_context, conversation)

    def _mock_decision(self, lead_context: dict[str, Any], conversation: list[dict[str, str]]) -> LeadDecision:
        last_msg = conversation[-1]["content"].lower() if conversation else ""
        if "appointment" in last_msg or "schedule" in last_msg or "book" in last_msg:
            return LeadDecision(
                intent="book_appointment",
                qualification_status="qualified",
                confidence=0.85,
                next_action="offer_appointment",
                reason="Lead expressed interest in scheduling",
                response="I can help you book an appointment. Here are available times.",
                appointment_requested=True,
            )
        if "not interested" in last_msg or "stop" in last_msg:
            return LeadDecision(
                intent="opt_out",
                qualification_status="unqualified",
                confidence=0.9,
                next_action="add_note",
                reason="Lead opted out",
                response="Understood. We will not contact you further.",
                note="Lead opted out via message",
            )
        if len(conversation) >= 2:
            return LeadDecision(
                intent="qualified_buyer",
                qualification_status="qualified",
                confidence=0.8,
                next_action="offer_appointment",
                reason="Lead answered qualification questions positively",
                response="Great! Would you like to schedule a consultation?",
                appointment_requested=False,
                pipeline_stage="Qualified",
                tags_to_add=["ai-qualified"],
            )
        return LeadDecision(
            intent="initial_inquiry",
            qualification_status="unknown",
            confidence=0.6,
            next_action="ask_qualification",
            reason="Need more information to qualify lead",
            response="Thanks for reaching out! What service are you interested in and what timeline works for you?",
        )
