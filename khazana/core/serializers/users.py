"""User serializers."""
import re
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from khazana.core.utils import is_weak_password, EMAIL_REGEX


class Scopes(str, Enum):
    """Scopes."""

    me = "me"
    admin = "admin"
    transaction_read = "transaction_read"
    transaction_write = "transaction_write"


class UserOut(BaseModel):
    """User serializer."""

    username: str
    scopes: List[str]
    firstLogin: Optional[bool] = Field(False)

    @field_validator("scopes", mode="before")
    @classmethod
    def scopes_validator(cls, vals: str):
        """Validate scopes."""
        return [val.strip() for val in vals.split(",")]


class UserIn(BaseModel):
    """User Create serializer."""

    username: str
    password: str
    scopes: List[Scopes]


class UserSignupIn(BaseModel):
    """User Create serializer."""

    username: str
    password: str
    email: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        """Validate password."""
        if len(v) < 8:
            raise ValueError("Password length must be atleast 8 characters.")
        if len(v) > 72:
            raise ValueError(
                "Password length must be less than 72 characters."
            )
        result = is_weak_password(v)
        if result:
            raise ValueError(
                "Password is too weak. Password should "
                "include at least 1 uppercase, "
                "1 lowercase, 1 number and "
                "1 special character."
            )
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        """Validate email."""
        if len(v) > 100:
            raise ValueError("Email length must be less than 100 characters.")
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Invalid email format.")
        return v


class ChangePasswordIn(BaseModel):
    """The incoming account settings model."""

    oldPassword: str = Field(...)
    newPassword: str = Field(...)
    emailAddress: str = Field(..., max_length=100)

    @field_validator("newPassword")
    @classmethod
    def check_length(cls, v: str):
        """Validate password."""
        if len(v) < 8:
            raise ValueError("Password length must be atleast 8 characters.")
        if len(v) > 72:
            raise ValueError(
                "Password length must be less than 72 characters."
            )
        result = is_weak_password(v)
        if result:
            raise ValueError(
                "Password is too weak. Password should "
                "include at least 1 uppercase, "
                "1 lowercase, 1 number and "
                "1 special character."
            )
        return v


class UserUpdate(BaseModel):
    """User update serializer."""

    username: str
    scopes: List[Scopes]
