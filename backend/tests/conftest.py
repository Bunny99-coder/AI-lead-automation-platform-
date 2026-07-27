import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("GHL_USE_MOCK", "true")
os.environ.setdefault("ELEVENLABS_USE_MOCK", "true")
os.environ.setdefault("WEBHOOK_SECRET", "dev-webhook-secret")
os.environ.setdefault("OPENAI_API_KEY", "")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_engine, get_session_factory, get_db
from app.main import create_app


@pytest.fixture(scope="function", autouse=True)
def fresh_db():
    get_settings.cache_clear()
    get_engine.cache_clear()
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture
def db_session(fresh_db):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=fresh_db)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def webhook_headers():
    return {"X-Webhook-Secret": "dev-webhook-secret"}


@pytest.fixture
def elevenlabs_headers():
    return {"X-ElevenLabs-Secret": "dev-elevenlabs-secret"}


@pytest.fixture
def sample_ghl_payload():
    return {
        "type": "ContactCreate",
        "id": "evt-001",
        "locationId": "loc-123",
        "contact": {
            "id": "contact-abc-001",
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane@example.com",
            "phone": "+15551234567",
        },
        "message": "Hi, I am interested in your services",
        "pipelineStage": "New Lead",
    }
