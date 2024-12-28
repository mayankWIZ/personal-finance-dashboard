from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_dashboard_data(auth_client: TestClient, db_session: Session):
    """Test getting dashboard data."""

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

    # Get dashboard data
    response = auth_client.get("/api/transactions/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "totalSavings" in data
    assert "monthlyExpenses" in data
    assert "investmentGrowth" in data
