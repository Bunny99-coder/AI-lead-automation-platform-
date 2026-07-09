from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Lead Automation Platform"
    debug: bool = False
    database_url: str = "postgresql://postgres:postgres@db:5432/leads"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ghl_api_key: str = ""
    ghl_location_id: str = ""
    ghl_calendar_id: str = ""
    ghl_base_url: str = "https://services.leadconnectorhq.com"
    ghl_use_mock: bool = True
    elevenlabs_api_key: str = ""
    elevenlabs_agent_id: str = ""
    elevenlabs_use_mock: bool = True
    webhook_secret: str = "dev-webhook-secret"
    elevenlabs_tool_secret: str = "dev-elevenlabs-secret"
    api_timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_base_delay_seconds: float = 1.0
    follow_up_max_retries: int = 3
    cors_origins: str = "http://localhost:5173,http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
