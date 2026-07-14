"""
database.py

SQLAlchemy database configuration.

Author: Shikhar Chauhan
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "receipts.db"

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# ==========================================================
# SQLAlchemy Engine
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

# ==========================================================
# Dependency
# ==========================================================

def get_db():
    """
    FastAPI database dependency.

    Usage:

        db: Session = Depends(get_db)
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================================
# Utility
# ==========================================================

def create_database():
    """
    Creates all database tables.
    """

    from api.database.models import Base

    Base.metadata.create_all(bind=engine)