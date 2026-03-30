from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
import os

# Use an environment variable for the database URL, with a SQLite in-memory fallback for testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")

# For SQLite, we need to configure StaticPool to prevent issues with multiple threads
# trying to use the same connection, especially in testing scenarios.
# For other databases (like PostgreSQL), StaticPool is not typically needed.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
