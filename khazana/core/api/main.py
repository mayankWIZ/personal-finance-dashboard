import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from passlib.context import CryptContext

from khazana.core.utils.database import engine, DBBaseModel, SessionLocal
from khazana.core.models import UserDB
from .routers import auth, users

API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.environ["JWT_SECRET"] = "secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
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


app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
