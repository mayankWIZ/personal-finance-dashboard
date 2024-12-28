"""Fetch latest exchange rates and symbols."""

import os
import copy
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


def change_base_currency_exchange_rates(
    old_rates: dict, old_base: str, new_base: str
) -> dict:
    """Change base currency in exchange rates."""
    rates = copy.deepcopy(old_rates)
    if old_base not in rates:
        raise ValueError(f"Unknown base currency: {old_base}")
    if new_base not in rates:
        raise ValueError(f"Unknown base currency: {new_base}")
    for currency, rate in rates.items():
        rates[currency] = round(
            rate / rates[old_base] * rates[new_base],
            4
        )
    return rates
