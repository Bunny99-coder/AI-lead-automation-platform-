import uuid

from app.core.logging import correlation_id_var


def set_correlation_id(value: str | None = None) -> str:
    cid = value or str(uuid.uuid4())
    correlation_id_var.set(cid)
    return cid


def get_correlation_id() -> str | None:
    return correlation_id_var.get()
