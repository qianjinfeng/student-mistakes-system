"""
Database connection and initialization
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import structlog

from config.settings import settings

logger = structlog.get_logger()

# SQLAlchemy sync engine for simplicity
engine = create_engine(
    settings.database.url,
    echo=settings.api.debug,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database connection and create tables"""
    try:
        # Create tables if they don't exist

        # Import all models to ensure they are registered
        from models import base

        # Create all tables
        base.Base.metadata.create_all(bind=engine)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


def close_db():
    """Close database connections"""
    engine.dispose()
    logger.info("Database connections closed")