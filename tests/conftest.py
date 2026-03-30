import pytest
import os
import importlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database import Base
from backend.database import get_db
from backend.main import app

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    db_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine(db_url, connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
                           poolclass=StaticPool if "sqlite" in db_url else None)
    # Auto-import all models to register with Base.metadata
    models_path = "app/models"
    if os.path.isdir(models_path):
        for root, dirs, files in os.walk(models_path):
            dirs[:] = sorted(dirs)
            files = sorted(files)
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    rel = os.path.relpath(os.path.join(root, file), ".").replace(os.sep, ".").removesuffix(".py")
                    try:
                        importlib.import_module(rel)
                    except Exception:
                        pass
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def session(setup_db):
    engine = setup_db
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    s = TestSession()
    yield s
    s.close()

@pytest.fixture(autouse=True)
def override_db(session):
    def _get_db_override():
        yield session
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(session):
    def _get_db_override():
        yield session
    app.dependency_overrides[get_db] = _get_db_override
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
