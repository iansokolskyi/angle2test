import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.core.dependencies import get_session
from app.main import app
from .utils import load_fixtures

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
DB_FILENAME = "test.db"
DATABASE_URL = f"sqlite:///./{DB_FILENAME}"

ADMIN_USER_ID = "1"
TEACHER_USER_ID = "4"


@pytest.fixture(scope="session", name="session")
def session_fixture():
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    # Delete the database
    SQLModel.metadata.drop_all(bind=engine)
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)


@pytest.fixture(scope="session", name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    load_fixtures(FIXTURES_DIR, session)

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
