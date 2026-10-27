import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ----------------------------------------------------------------------
# Database URL – defaults to a local SQLite file.
# Override via the environment variable DATABASE_URL (e.g. Postgres) if needed.
# ----------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kisansaarthi.db")

# ----------------------------------------------------------------------
# Engine – for SQLite we need `check_same_thread=False` so the same
# connection can be used across different FastAPI request threads.
# ----------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# ----------------------------------------------------------------------
# Session factory – each request gets its own Session instance.
# ----------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models.
Base = declarative_base()


# ----------------------------------------------------------------------
# Dependency for FastAPI routes – yields a Session and ensures it is closed.
# ----------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------------------
# Helper to create tables from model definitions.
# ----------------------------------------------------------------------
def init_db():
    """Create all tables defined in `backend.app.db.models`."""
    from backend.app.db import models  # Imported lazily to avoid circular imports
    Base.metadata.create_all(bind=engine)


# ----------------------------------------------------------------------
# Auto‑initialize SQLite tables on import (fails silently for non‑SQLite backends).
# ----------------------------------------------------------------------
try:
    init_db()
except Exception as _e:
    pass