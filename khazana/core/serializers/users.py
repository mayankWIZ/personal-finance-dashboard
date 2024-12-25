"""User serializers."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


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


class ChangePasswordIn(BaseModel):
    """The incoming account settings model."""

    oldPassword: str = Field(...)
    newPassword: str = Field(...)
    emailAddress: str = Field(..., max_length=100)

    @field_validator("newPassword")
    @classmethod
    def check_length(cls, v: str, info):
        """Validate password."""
        if len(v) < 8:
            raise ValueError("Password length must be atleast 8 characters.")
        if len(v) > 72:
            raise ValueError(
                "Password length must be less than 72 characters."
            )
        return v


class UserUpdate(BaseModel):
    """User update serializer."""

    username: str
    scopes: List[Scopes]
