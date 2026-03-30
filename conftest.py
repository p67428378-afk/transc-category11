import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from main import app
from database import Base, get_db
from models import PolicyHolder, Vehicle, Policy, NCBTier

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

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
    del app.dependency_overrides[get_db]

@pytest.fixture
def setup_ncb_tiers(session):
    # Setup default NCB tiers for testing
    tiers_data = [
        NCBTier(ncbYears=0, discountPercentage=0.0),
        NCBTier(ncbYears=1, discountPercentage=0.20),
        NCBTier(ncbYears=2, discountPercentage=0.25),
        NCBTier(ncbYears=3, discountPercentage=0.30),
        NCBTier(ncbYears=4, discountPercentage=0.40),
        NCBTier(ncbYears=5, discountPercentage=0.50),
    ]
    session.add_all(tiers_data)
    session.commit()
    return tiers_data
