"""Configuration for pytest."""

import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from khazana.core.database import DBBaseModel
from khazana.core.apis.main import app
from khazana.core.models import UserDB
from khazana.core.utils import get_password_hash

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DBBaseModel.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """Get FastAPI test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def first_time_auth_client():
    """Get FastAPI test client for first time login."""
    with TestClient(app) as client:
        response = client.post(
            "/api/auth", data={"username": "admin", "password": "admin"}
        )
        token = response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client


@pytest.fixture(scope="module")
def auth_client():
    """Get FastAPI test client."""
    with TestClient(app) as client:
        response = client.post(
            "/api/auth", data={"username": "admin", "password": "Admin@123"}
        )
        token = response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client


@pytest.fixture(scope="module")
def db_session():
    """Database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# def pytest_sessionstart(session):
#     """
#     Initialize session.

#     Args:
#         session: The session object.

#     Returns:
#         None.
#     """
#     CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#     # allow import of `khazana`
#     sys.path.append(CODE_DIR)
