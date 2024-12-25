"""Exchange rates related database models."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, UUID, Column, DateTime, String, ForeignKey

from khazana.core.database import DBBaseModel


class ExchangeRateSymbolDB(DBBaseModel):
    """Exchange rate symbol database model."""

    __tablename__ = "exchange_rate_symbols"

    symbol = Column(String, nullable=False, primary_key=True, index=True)
    fullName = Column(String, nullable=False, index=False)
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))


class ExchangeRatesDB(DBBaseModel):
    """Exchange rates database model."""

    __tablename__ = "exchange_rates"

    id = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    base = Column(
        String, ForeignKey("exchange_rate_symbols.symbol"), nullable=False
    )
    last_updated = Column(DateTime, default=datetime.now(timezone.utc))
    rates = Column(JSON, nullable=True)
