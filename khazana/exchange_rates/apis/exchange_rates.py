"""Transaction related Endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Union

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from khazana.core.database import get_db
from khazana.core.models import UserDB
from khazana.core.utils import get_current_user

from ..models import ExchangeRatesDB, ExchangeRateSymbolDB
from ..serializers import ExchangeRatesOut, ExchangeRateSymbolOut
from ..utils import (
    EXCHANGE_RATE_EXPIRE_MINUTES,
    fetch_exchange_rate_symbols,
    fetch_exchange_rates,
    change_base_currency_exchange_rates,
)

router = APIRouter(tags=["Exchange Rates"])


@router.get(
    "",
    description="Get list of exchange rates.",
    response_model=ExchangeRatesOut,
)
def list_exchange_rates(
    db: Session = Depends(get_db),
    _: UserDB = Security(get_current_user, scopes=["me"]),
) -> ExchangeRatesOut:
    """List transactions."""
    are_rates_expired = False
    rate = (
        db.query(ExchangeRatesDB)
        .order_by(ExchangeRatesDB.last_updated.desc())
        .first()
    )
    if not rate:
        are_rates_expired = True
    elif rate.last_updated < (
        datetime.now(timezone.utc)
        - timedelta(minutes=EXCHANGE_RATE_EXPIRE_MINUTES)
    ).replace(tzinfo=None):
        are_rates_expired = True
    if are_rates_expired:
        exchange_rate_symbols = fetch_exchange_rate_symbols()
        existing_symbols = {
            symbol.symbol: symbol
            for symbol in db.query(ExchangeRateSymbolDB).all()
        }
        for symbol, full_name in exchange_rate_symbols["symbols"].items():
            if symbol in existing_symbols:
                existing_symbols[symbol].last_updated = datetime.now(
                    timezone.utc
                )
                db.add(existing_symbols[symbol])
            else:
                db.add(ExchangeRateSymbolDB(symbol=symbol, fullName=full_name))
        db.commit()
        exchange_rates = fetch_exchange_rates()
        if not rate:
            rate = ExchangeRatesDB(
                base="USD",
                last_updated=datetime.now(timezone.utc),
                rates=exchange_rates["rates"],
            )
        else:
            rate.base = "USD"
            rate.last_updated = datetime.now(timezone.utc)
            rate.rates = exchange_rates["rates"]
        db.add(rate)
        db.commit()
        db.refresh(rate)

    rate.rates = change_base_currency_exchange_rates(
        rate.rates, rate.base, "USD"
    )
    return ExchangeRatesOut(**rate.__dict__)


@router.get(
    "/symbols",
    description="Get list of exchange rate symbols.",
    # response_model=List[ExchangeRateSymbolOut],
)
def list_exchange_rate_symbols(
    db: Session = Depends(get_db),
    _: UserDB = Security(get_current_user, scopes=["me"]),
) -> Dict[str, Union[List[ExchangeRateSymbolOut], int]]:
    """List exchange rate symbols."""
    symbols = db.query(ExchangeRateSymbolDB).all()
    result = [ExchangeRateSymbolOut(**symbol.__dict__) for symbol in symbols]
    return {
        "symbols": result,
        "count": len(result),
    }
