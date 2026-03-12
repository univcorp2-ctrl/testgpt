from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import AppSettings


def get_engine(settings: AppSettings):
    return create_engine(settings.db_dsn, pool_pre_ping=True)


def get_session_factory(settings: AppSettings) -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(settings), expire_on_commit=False, class_=Session)
