"""Test users module."""

import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_no_any_other_api_call_allowed(
    first_time_auth_client: TestClient, db_session: Session
):
    """Test no other api call allowed."""
    response = first_time_auth_client.get("/api/transactions")
    assert response.status_code == 401


def test_change_password(first_time_auth_client: TestClient, db_session: Session):
    """Test changing the password."""
    response = first_time_auth_client.patch(
        "/api/users/change_password",
        json={
            "oldPassword": "admin",
            "newPassword": "Admin@123",
            "emailAddress": "admin@example.com",
        },
    )
    assert response.status_code == 200


def test_create_user(auth_client: TestClient, db_session: Session):
    """Test creating a new user."""
    response = auth_client.post(
        "/api/users",
        json={
            "fullName": "Test User",
            "username": "testuser",
            "password": "Test@1234",
            "emailAddress": "testuser@example.com",
            "scopes": ["me"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["emailAddress"] == "testuser@example.com"


def test_get_user(auth_client: TestClient, db_session: Session):
    """Test getting a user."""
    unique_user = {
        "username": f"testuser{random.randint(1, 100)}",
        "emailAddress": f"testuser{random.randint(1, 100)}@example.com",
    }
    response = auth_client.post(
        "/api/users",
        json={
            "fullName": "Test User",
            "username": unique_user["username"],
            "password": "Test@1234",
            "emailAddress": unique_user["emailAddress"],
            "scopes": ["me"],
        },
    )
    assert response.status_code == 200
    data = response.json()

    response = auth_client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert unique_user["username"] in [user["username"] for user in data]
    assert unique_user["emailAddress"] in [user["emailAddress"] for user in data]


def test_update_user(auth_client: TestClient, db_session: Session):
    """Test updating a user."""
    unique_user = {
        "username": f"testuser{random.randint(1, 100)}",
        "emailAddress": f"testuser{random.randint(1, 100)}@example.com",
    }
    response = auth_client.post(
        "/api/users",
        json={
            "fullName": "Test User",
            "username": unique_user["username"],
            "password": "Test@1234",
            "emailAddress": unique_user["emailAddress"],
            "scopes": ["me"],
        },
    )
    assert response.status_code == 200
    data = response.json()

    user_update = {
        "username": unique_user["username"],
        "fullName": "Updated User",
        "emailAddress": "updateduser@example.com",
        "scopes": ["me", "transaction_read"],
    }
    response = auth_client.patch("/api/users", json=user_update)
    assert response.status_code == 200
    data = response.json()
    assert data["fullName"] == "Updated User"
    assert data["emailAddress"] == "updateduser@example.com"
    assert data["scopes"] == ["me", "transaction_read"]


def test_delete_user(auth_client: TestClient, db_session: Session):
    """Test deleting a user."""
    unique_user = {
        "username": f"testuser{random.randint(1, 100)}",
        "emailAddress": f"testuser{random.randint(1, 100)}@example.com",
    }
    response = auth_client.post(
        "/api/users",
        json={
            "fullName": "Test User",
            "username": unique_user["username"],
            "password": "Test@1234",
            "emailAddress": unique_user["emailAddress"],
            "scopes": ["me"],
        },
    )
    assert response.status_code == 200
    data = response.json()

    response = auth_client.delete(
        "/api/users", params={"username": unique_user["username"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
