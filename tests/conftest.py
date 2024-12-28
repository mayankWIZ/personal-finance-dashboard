"""Configuration for pytest."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from khazana.core.database import DBBaseModel
from khazana.core.apis.main import app

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DBBaseModel.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def setup():
    """Initialize setup."""
    os.environ["JWT_SECRET"] = "secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
    yield


@pytest.fixture(scope="module", autouse=True)
def client(setup):
    """Get FastAPI test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def first_time_auth_client(setup):
    """Get FastAPI test client for first time login."""
    with TestClient(app) as client:
        response = client.post(
            "/api/auth", data={"username": "admin", "password": "admin"}
        )
        token = response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client


@pytest.fixture(scope="module")
def auth_client(setup):
    """Get FastAPI test client."""
    with TestClient(app) as client:
        response = client.post(
            "/api/auth", data={"username": "admin", "password": "Admin@123"}
        )
        token = response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client


@pytest.fixture(scope="module")
def db_session(setup):
    """Database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
