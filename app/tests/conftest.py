import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.core.dependencies import get_db
from app.main import app
from .utils import load_fixtures

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
DB_FILENAME = "test.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///./{DB_FILENAME}"

ADMIN_USER_ID = "1"
TEACHER_USER_ID = "4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


@pytest.fixture(scope="session")
def db_session():
    # Create the database

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)


@pytest.fixture(scope="session")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    load_fixtures(FIXTURES_DIR, db_session)

    yield TestClient(app)
