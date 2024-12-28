"""Test transactions module."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from khazana.core.models import UserDB
from khazana.transactions.models import TransactionDB
from uuid import uuid4


def test_create_transaction(auth_client: TestClient, db_session: Session):
    """Test creating a new transaction."""
    transaction = {
        "description": "Test Transaction",
        "amount": 100.0,
        "category": "Test Category",
        "transactionDate": "2023-12-01T00:00:00Z",
        "transactionType": "income",
    }

    response = auth_client.post("/api/transactions", json=transaction)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test Transaction"
    assert data["amount"] == 100.0


def test_update_transaction(auth_client: TestClient, db_session: Session):
    """Test updating a transaction."""
    transaction = {
        "description": "Test Transaction",
        "amount": 100.0,
        "category": "Test Category",
        "transactionDate": "2023-12-01T00:00:00Z",
        "transactionType": "income",
    }

    response = auth_client.post("/api/transactions", json=transaction)
    assert response.status_code == 200
    transaction_id = response.json()["id"]

    transaction_update = {"description": "Updated Transaction", "amount": 150.0}

    response = auth_client.patch(
        f"/api/transactions/{str(transaction_id)}", json=transaction_update
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Transaction"
    assert data["amount"] == 150.0


def test_delete_transaction(auth_client: TestClient, db_session: Session):
    """Test deleting a transaction."""
    transaction = {
        "description": "Test Transaction",
        "amount": 100.0,
        "category": "Test Category",
        "transactionDate": "2023-12-01T00:00:00Z",
        "transactionType": "income",
    }

    response = auth_client.post("/api/transactions", json=transaction)
    assert response.status_code == 200
    transaction_id = response.json()["id"]

    response = auth_client.delete(f"/api/transactions/{str(transaction_id)}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
