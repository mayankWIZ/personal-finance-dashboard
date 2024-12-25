"""Main API module."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from passlib.context import CryptContext
from pydantic import BaseModel

from khazana.core.database import DBBaseModel, SessionLocal, engine
from khazana.core.models import UserDB

from ...exchange_rates import apis as exchange_rates_router
from ...transactions import apis as transactions_router
from . import auth, users


class ErrorMessage(BaseModel):
    """Error message model."""

    detail: str


API_PREFIX = "/api"
MODULES = {
    "transactions": transactions_router.routers,
    "exchange-rates": exchange_rates_router.routers,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler."""
    os.environ["JWT_SECRET"] = "secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["EXCHANGE_RATE_API_KEY"] = "9e9ecae8b8ca62d01fc22f16e4460333"
    DBBaseModel.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user = db.query(UserDB).filter(UserDB.username == "admin").first()
        if not user:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            db.add(
                UserDB(
                    username="admin",
                    hashed_password=pwd_context.hash("admin"),
                    scopes="admin,me,transaction_read,transaction_write",
                )
            )
            db.commit()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Personal Finance Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
common_responses = {
    "400": {"model": ErrorMessage},
    "401": {"model": ErrorMessage},
    "403": {"model": ErrorMessage},
    "405": {"model": ErrorMessage},
    "429": {"model": ErrorMessage},
    "500": {"model": ErrorMessage},
}

app.include_router(auth.router, responses=common_responses, prefix=API_PREFIX)
app.include_router(users.router, responses=common_responses, prefix=API_PREFIX)

# loading integration specific routers
for prefix, routers in MODULES.items():
    for router in routers:
        app.include_router(
            router, responses=common_responses, prefix=f"{API_PREFIX}/{prefix}"
        )
