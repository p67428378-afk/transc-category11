import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base_class import Base


# Use DATABASE_URL from environment, or fallback to in-memory SQLite for testing/development
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")


if SQLALCHEMY_DATABASE_URL == "sqlite:///:memory:":
    # Use StaticPool for SQLite in-memory to prevent losing tables between requests
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

def init_db():
    # Import all models here so that Base.metadata.create_all can find them
    from app.models import kyc  # noqa: F401
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
