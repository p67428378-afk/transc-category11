import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import uuid

from main import app
from database import Base, get_db
from models import Category, CustomMapping, PreseededMapping, Transaction, Budget

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool, # Use StaticPool to keep the same connection for all tests
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine) # Create tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) # Drop tables after tests

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_data(session):
    # Create some categories
    category_food = Category(category_id=str(uuid.uuid4()), name="Food & Drink")
    category_entertainment = Category(category_id=str(uuid.uuid4()), name="Entertainment")
    category_utilities = Category(category_id=str(uuid.uuid4()), name="Utilities")
    session.add_all([category_food, category_entertainment, category_utilities])
    session.commit()
    session.refresh(category_food)
    session.refresh(category_entertainment)
    session.refresh(category_utilities)

    # Create some pre-seeded mappings
    preseeded_starbucks = PreseededMapping(mapping_id=str(uuid.uuid4()), merchant_keyword="Starbucks", category_id=category_food.category_id)
    preseeded_netflix = PreseededMapping(mapping_id=str(uuid.uuid4()), merchant_keyword="Netflix", category_id=category_entertainment.category_id)
    session.add_all([preseeded_starbucks, preseeded_netflix])
    session.commit()
    session.refresh(preseeded_starbucks)
    session.refresh(preseeded_netflix)

    return {
        "category_food": category_food,
        "category_entertainment": category_entertainment,
        "category_utilities": category_utilities,
        "preseeded_starbucks": preseeded_starbucks,
        "preseeded_netflix": preseeded_netflix,
    }
