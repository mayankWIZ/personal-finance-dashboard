from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_list_exchange_rates(auth_client: TestClient, db_session: Session):
    """Test listing exchange rates."""
    response = auth_client.get("/api/exchange-rates")
    assert response.status_code == 200
    data = response.json()
    assert "rates" in data
    assert "base" in data
    assert "last_updated" in data


def test_list_exchange_rate_symbols(auth_client: TestClient, db_session: Session):
    """Test listing exchange rate symbols."""
    response = auth_client.get("/api/exchange-rates/symbols")
    assert response.status_code == 200
    data = response.json()
    assert "symbols" in data
    assert "count" in data
    assert data["count"] > 0

    symbol = data["symbols"][0]
    assert "symbol" in symbol
    assert "fullName" in symbol
