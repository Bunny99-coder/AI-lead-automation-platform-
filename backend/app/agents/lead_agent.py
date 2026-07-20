import logging
from typing import Any

from sqlalchemy.orm import Session

from app.agents.policy import ActionType, is_action_allowed
from app.agents.tools import validate_tool_args
from app.integrations.openai.client import OpenAIClient
from app.models.ai_action import AIAction
from app.models.lead import Lead, LeadStatus, QualificationStatus
from app.schemas.ai import LeadDecision, NextAction
from app.services.appointment_service import AppointmentService
from app.services.follow_up_service import FollowUpService
from app.services.lead_service import LeadService
from app.services.message_service import MessageService
from app.utils.correlation import get_correlation_id

logger = logging.getLogger(__name__)


class LeadQualificationAgent:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.lead_service = LeadService(db)
        self.message_service = MessageService(db)
        self.appointment_service = AppointmentService(db)
        self.follow_up_service = FollowUpService(db)
        self.openai = OpenAIClient()

    async def process_lead(self, lead_id: int) -> LeadDecision:
        lead = self.lead_service.get_lead_or_raise(lead_id)
        conversation = self.message_service.get_conversation_history(lead_id)
        context = {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "pipeline_stage": lead.pipeline_stage,
            "qualification_status": lead.qualification_status.value,
        }
        decision = await self.openai.qualify_lead(context, conversation)
        await self._execute_decision(lead, decision)
        return decision

    async def _execute_decision(self, lead: Lead, decision: LeadDecision) -> None:
        self._record_action(lead.id, "decision", None, decision.model_dump(), True)

        qual_map = {
            "qualified": QualificationStatus.QUALIFIED,
            "unqualified": QualificationStatus.UNQUALIFIED,
            "needs_review": QualificationStatus.NEEDS_REVIEW,
            "unknown": QualificationStatus.UNKNOWN,
        }
        if decision.qualification_status in qual_map:
            if is_action_allowed(ActionType.UPDATE_QUALIFICATION):
                self.lead_service.update_qualification(lead, qual_map[decision.qualification_status])

        if decision.note and is_action_allowed(ActionType.ADD_NOTE):
            await self.execute_tool("add_lead_note", {"lead_id": lead.id, "note": decision.note})

        for tag in decision.tags_to_add:
            if is_action_allowed(ActionType.ADD_TAG):
                await self.execute_tool("add_tag", {"lead_id": lead.id, "tag": tag})

        if decision.pipeline_stage and is_action_allowed(ActionType.MOVE_PIPELINE):
            await self.execute_tool(
                "change_pipeline_stage", {"lead_id": lead.id, "stage": decision.pipeline_stage}
            )

        if decision.next_action == NextAction.SEND_MESSAGE and decision.response:
            await self.execute_tool(
                "send_message", {"lead_id": lead.id, "message": decision.response, "channel": "sms"}
            )
        elif decision.next_action == NextAction.OFFER_APPOINTMENT:
            slots = await self.execute_tool("get_available_appointments", {"lead_id": lead.id})
            if decision.response:
                await self.execute_tool(
                    "send_message",
                    {
                        "lead_id": lead.id,
                        "message": decision.response,
                        "channel": "sms",
                    },
                )
            lead.status = LeadStatus.QUALIFYING
            self.db.commit()
            self._record_action(lead.id, "offer_appointment", "get_available_appointments", slots, True)
        elif decision.next_action == NextAction.BOOK_APPOINTMENT and decision.preferred_slot_id:
            await self.execute_tool(
                "book_appointment", {"lead_id": lead.id, "slot_id": decision.preferred_slot_id}
            )
        elif decision.next_action == NextAction.SCHEDULE_FOLLOW_UP:
            await self.execute_tool(
                "create_follow_up",
                {"lead_id": lead.id, "delay_hours": 24, "message": decision.response},
            )
        elif decision.next_action == NextAction.ESCALATE_HUMAN:
            lead.status = LeadStatus.FOLLOW_UP
            self.db.commit()

    async def execute_tool(self, tool_name: str, args: dict[str, Any], confirmed: bool = False) -> Any:
        validated = validate_tool_args(tool_name, args)
        action_map = {
            "add_lead_note": ActionType.ADD_NOTE,
            "add_tag": ActionType.ADD_TAG,
            "update_lead": ActionType.UPDATE_QUALIFICATION,
            "change_pipeline_stage": ActionType.MOVE_PIPELINE,
            "create_follow_up": ActionType.SCHEDULE_FOLLOW_UP,
            "send_message": ActionType.SEND_MESSAGE,
            "book_appointment": ActionType.BOOK_APPOINTMENT,
            "get_available_appointments": ActionType.GET_AVAILABILITY,
        }
        action_type = action_map.get(tool_name)
        if action_type and not is_action_allowed(action_type, confirmed=confirmed):
            raise PermissionError(f"Action {tool_name} requires confirmation")

        try:
            result = await self._dispatch_tool(tool_name, validated.model_dump())
            self._record_action(validated.lead_id, tool_name, tool_name, args, True, output=result)  # type: ignore[attr-defined]
            return result
        except Exception as exc:
            logger.exception("Tool execution failed: %s", tool_name)
            lead_id = getattr(validated, "lead_id", None)
            if lead_id:
                self._record_action(lead_id, tool_name, tool_name, args, False, error=str(exc))
            raise

    async def _dispatch_tool(self, tool_name: str, args: dict[str, Any]) -> Any:
        lead_id = args["lead_id"]
        lead = self.lead_service.get_lead_or_raise(lead_id)

        if tool_name == "get_lead":
            return self.lead_service.lead_to_dict(lead)
        if tool_name == "update_lead":
            return self.lead_service.update_lead_fields(lead, args)
        if tool_name == "add_lead_note":
            return await self.lead_service.add_note(lead, args["note"])
        if tool_name == "change_pipeline_stage":
            return await self.lead_service.change_pipeline(lead, args["stage"])
        if tool_name == "add_tag":
            return await self.lead_service.add_tag(lead, args["tag"])
        if tool_name == "create_follow_up":
            return await self.follow_up_service.schedule_follow_up(
                lead, delay_hours=args["delay_hours"], message=args.get("message")
            )
        if tool_name == "get_available_appointments":
            return await self.appointment_service.get_availability_for_lead(lead)
        if tool_name == "book_appointment":
            return await self.appointment_service.book_appointment(lead, args["slot_id"])
        if tool_name == "send_message":
            return await self.message_service.send_to_lead(
                lead, args["message"], channel=args["channel"]
            )
        raise ValueError(f"Unhandled tool: {tool_name}")

    def _record_action(
        self,
        lead_id: int,
        action_type: str,
        tool_used: str | None,
        input_data: dict | None,
        success: bool,
        output: Any = None,
        error: str | None = None,
    ) -> None:
        action = AIAction(
            lead_id=lead_id,
            action_type=action_type,
            tool_used=tool_used,
            input_data=input_data,
            output_data=output if isinstance(output, dict) else {"result": output},
            success=success,
            error=error,
            correlation_id=get_correlation_id(),
        )
        self.db.add(action)
        self.db.commit()
