import jwt
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jwt import PyJWTError

from khazana.core import PASSWORD_PATTERN
from ..models.user import UserDB
from .database import get_db

ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth",
    scopes={
        "me": "Change account settings.",
        "admin": "Admin access.",
        "transaction_read": "Read Transaction.",
        "transaction_write": "Write Transaction.",
    },
)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token."""
    # Secret key and algorithm for JWT
    SECRET_KEY = os.environ["JWT_SECRET"]
    ALGORITHM = os.environ["JWT_ALGORITHM"]
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _get_current_user(
    security_scopes: SecurityScopes,
    token: str,
    db: Session,
    allow_on_first_login: bool = False,
) -> UserDB:
    """Get current user.

    Args:
        security_scopes (SecurityScopes): Security scopes required.
        token (str, optional): JWT Token. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: On authorization failure.

    Returns:
        User: The owner of the token.
    """
    # Secret key and algorithm for JWT
    SECRET_KEY = os.environ["JWT_SECRET"]
    ALGORITHM = os.environ["JWT_ALGORITHM"]

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        scopes = payload.get("scopes", [])
        for scope in security_scopes.scopes:
            if scope not in scopes:
                raise HTTPException(403, "Not enough permissions.")
        user: UserDB = db.query(UserDB).filter(UserDB.username == username).first()
        if not user:
            raise HTTPException(401, "Could not authenticate the user.")
        if user.firstLogin and not allow_on_first_login:
            raise HTTPException(401, "Change the password before using this endpoint.")
        return user
    except PyJWTError:
        raise credentials_exception


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserDB:
    return _get_current_user(security_scopes, token, db, allow_on_first_login=False)


async def get_current_user_first_login(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserDB:
    return _get_current_user(security_scopes, token, db, allow_on_first_login=True)


def is_weak_password(password):
    """Check if the password is aligned with password policy or not.

    Args:
        password (str): password of the user to check.

    Returns:
        bool: true if password is not aligned with password policy else false.
    """
    if password == "admin":
        return False
    return not bool(re.match(PASSWORD_PATTERN, password))


def get_password_hash(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def is_admin(user: UserDB) -> bool:
    return "admin" in user.scopes.split(",")
