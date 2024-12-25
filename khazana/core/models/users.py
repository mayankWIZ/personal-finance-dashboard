"""Provides user related models."""

from uuid import uuid4

from sqlalchemy import UUID, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from khazana.core.database import DBBaseModel


class UserDB(DBBaseModel):
    """User database model."""

    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, unique=True, index=True)
    emailAddress = Column(String, unique=True, nullable=True)
    hashed_password = Column(String)
    scopes = Column(String, default="user")
    firstLogin = Column(Boolean, default=True)
    createdBy = Column(
        UUID, ForeignKey("users.id"), nullable=True, default=None
    )

    transactions = relationship(
        "TransactionDB",
        back_populates="user",
        foreign_keys="TransactionDB.userId",
    )
