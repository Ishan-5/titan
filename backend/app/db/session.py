"""
Engine + session factory. This is the ONLY file that constructs the
SQLAlchemy engine — everything else imports get_db() and never touches
the connection string directly. Swapping SQLite for Supabase Postgres
later is just changing DATABASE_URL in .env; this file needs zero edits.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.models import Base

# SQLite needs this flag because FastAPI can use the same connection
# across threads; Postgres doesn't need it, so we only set it conditionally.
connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables if they don't exist yet. Fine at this scale —
    we'll move to Alembic migrations only if/when the schema needs
    versioning across environments."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yields a session, always closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()