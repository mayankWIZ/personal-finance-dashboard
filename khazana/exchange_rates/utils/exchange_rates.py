"""Fetch latest exchange rates and symbols."""

import os
import requests

from .const import (
    FETCH_EXCHANGE_RATES_ENDPOINT,
    FETCH_EXCHANGE_RATES_SYMBOLS_ENDPOINT,
)


def fetch_exchange_rates(base: str = "EUR") -> dict:
    """Fetch latest exchange rates."""
    response = requests.get(
        FETCH_EXCHANGE_RATES_ENDPOINT,
        params={
            "access_key": os.environ["EXCHANGE_RATE_API_KEY"],
            "base": base,
        },
    )
    response.raise_for_status()
    return response.json()


def fetch_exchange_rate_symbols() -> dict:
    """Fetch exchange rate symbols."""
    response = requests.get(
        FETCH_EXCHANGE_RATES_SYMBOLS_ENDPOINT,
        params={
            "access_key": os.environ["EXCHANGE_RATE_API_KEY"],
        },
    )
    response.raise_for_status()
    return response.json()
