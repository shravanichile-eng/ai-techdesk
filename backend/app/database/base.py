"""Database base configuration"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool, NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()

# Determine pool settings based on environment
if settings.ENVIRONMENT == "testing":
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )

# Enable pgvector extension
@event.listens_for(engine, "connect")
def enable_pgvector(dbapi_conn, connection_record):
    """Enable pgvector extension on connection"""
    try:
        cursor = dbapi_conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        dbapi_conn.commit()
        logger.info("pgvector extension enabled")
    except Exception as e:
        logger.warning(f"Could not enable pgvector: {e}")
        dbapi_conn.rollback()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """Dependency for database session injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
