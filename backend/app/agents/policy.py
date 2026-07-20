from enum import Enum


class ActionType(str, Enum):
    ADD_NOTE = "add_note"
    ADD_TAG = "add_tag"
    UPDATE_QUALIFICATION = "update_qualification"
    MOVE_PIPELINE = "move_pipeline"
    SCHEDULE_FOLLOW_UP = "schedule_follow_up"
    SEND_MESSAGE = "send_message"
    BOOK_APPOINTMENT = "book_appointment"
    GET_AVAILABILITY = "get_availability"
    UPDATE_CONTACT = "update_contact"
    CANCEL_APPOINTMENT = "cancel_appointment"
    DELETE_DATA = "delete_data"


AUTO_ALLOWED = {
    ActionType.ADD_NOTE,
    ActionType.ADD_TAG,
    ActionType.UPDATE_QUALIFICATION,
    ActionType.MOVE_PIPELINE,
    ActionType.SCHEDULE_FOLLOW_UP,
    ActionType.SEND_MESSAGE,
    ActionType.BOOK_APPOINTMENT,
    ActionType.GET_AVAILABILITY,
}

REQUIRES_CONFIRMATION = {
    ActionType.CANCEL_APPOINTMENT,
    ActionType.DELETE_DATA,
    ActionType.UPDATE_CONTACT,
}


def is_action_allowed(action: ActionType, confirmed: bool = False) -> bool:
    if action in AUTO_ALLOWED:
        return True
    if action in REQUIRES_CONFIRMATION:
        return confirmed
    return False
