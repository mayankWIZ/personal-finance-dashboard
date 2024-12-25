"""Exchange rates serializers."""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class ExchangeRateSymbolOut(BaseModel):
    """Exchange rate symbol model."""

    symbol: str
    fullName: str


class ExchangeRatesOut(BaseModel):
    """Exchange rates out model."""

    base: str
    last_updated: Optional[datetime]
    rates: Dict[str, float]
