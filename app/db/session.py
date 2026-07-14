from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import DATABASE_URL

# Engine configuration for production
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=True)


def init_db() -> None:
    """Create all tables."""
    from app.db.models import Base
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_db() -> None:
    """Close connection pool on shutdown."""
    engine.dispose()