"""Transaction serializers."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ..utils import TransactionType


class TransactionIn(BaseModel):
    """Transaction model."""

    description: str = Field(...)
    amount: float = Field(
        ...,
        description=(
            "If transactionType is not investment it will be "
            "considered as either expense or income based on "
            "the amount."
        ),
    )
    category: str = Field(...)
    transactionDate: datetime = Field(datetime.now(timezone.utc))
    transactionType: Optional[TransactionType] = Field(TransactionType.expense)

    @field_validator("transactionDate")
    @classmethod
    def validate_transaction_date(cls, v: datetime):
        """Validate transaction date."""
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > datetime.now(timezone.utc):
            raise ValueError("Transaction date can not be in the future.")
        return v


class TransactionOut(TransactionIn):
    """Transaction out model."""

    id: UUID = Field(...)

    @field_validator("transactionDate")
    @classmethod
    def validate_transaction_date(cls, v: datetime):
        """Override transaction date validation."""
        return v


class TransactionUpdate(BaseModel):
    """Transaction update model."""

    description: Optional[str] = Field(None)
    amount: Optional[float] = Field(
        None,
        description=(
            "If transactionType is not investment it will be "
            "considered as either expense or income based on "
            "the amount."
        ),
    )
    category: Optional[str] = Field(None)
    transactionDate: Optional[datetime] = Field(None)
    transactionType: Optional[TransactionType] = Field(None)

    @field_validator("transactionDate")
    @classmethod
    def validate_transaction_date(cls, v: datetime):
        """Validate transaction date."""
        if not v:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > datetime.now(timezone.utc):
            raise ValueError("Transaction date can not be in the future.")
        return v
