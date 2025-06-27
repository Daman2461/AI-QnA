from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Create SQLite engine with appropriate settings
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    poolclass=StaticPool  # Use static pool for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 