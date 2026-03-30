from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use DATABASE_URL environment variable, default to in-memory SQLite for local development/testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# For SQLite, we need to configure check_same_thread to False
# For PostgreSQL, this parameter is ignored
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
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
