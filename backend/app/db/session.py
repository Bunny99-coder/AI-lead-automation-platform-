from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base


@lru_cache
def get_engine():
    settings = get_settings()
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        pool_kwargs = {"poolclass": StaticPool}
    else:
        pool_kwargs = {}
    return create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args, **pool_kwargs)


def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


SessionLocal = get_session_factory  # backwards-compatible alias


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def get_db() -> Generator[Session, None, None]:
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()
