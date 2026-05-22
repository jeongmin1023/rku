from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./labfit.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    if DATABASE_URL.startswith("sqlite"):
        _ensure_sqlite_columns()


def _ensure_sqlite_columns() -> None:
    """Small MVP migration shim for local SQLite databases created before this schema."""

    with engine.begin() as connection:
        rows = connection.execute(text("PRAGMA table_info(master_papers)")).mappings().all()
        existing = {row["name"] for row in rows}
        for column, definition in {
            "merge_confidence": "FLOAT DEFAULT 0.5",
            "merge_notes_json": "TEXT",
            "source_confidence_signals_json": "TEXT",
        }.items():
            if column not in existing:
                connection.execute(text(f"ALTER TABLE master_papers ADD COLUMN {column} {definition}"))

        rows = connection.execute(text("PRAGMA table_info(analysis_results)")).mappings().all()
        existing = {row["name"] for row in rows}
        for column, definition in {
            "detailed_trend_summary": "TEXT",
            "trend_confidence": "VARCHAR(20) DEFAULT 'low'",
            "recent_important_papers_json": "TEXT",
            "interest_related_papers_json": "TEXT",
            "supporting_papers_json": "TEXT",
            "excluded_papers_count": "INTEGER DEFAULT 0",
        }.items():
            if column not in existing:
                connection.execute(text(f"ALTER TABLE analysis_results ADD COLUMN {column} {definition}"))
