import hmac
from hashlib import sha256

from fastapi import Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings


def verify_webhook_secret(
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
    settings: Settings = Depends(get_settings),
) -> None:
    if not x_webhook_secret or not hmac.compare_digest(x_webhook_secret, settings.webhook_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret")


def verify_elevenlabs_secret(
    x_elevenlabs_secret: str | None = Header(default=None, alias="X-ElevenLabs-Secret"),
    settings: Settings = Depends(get_settings),
) -> None:
    secret = settings.elevenlabs_tool_secret
    if not x_elevenlabs_secret or not hmac.compare_digest(x_elevenlabs_secret, secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ElevenLabs secret")


def hash_payload(payload: str) -> str:
    return sha256(payload.encode("utf-8")).hexdigest()
