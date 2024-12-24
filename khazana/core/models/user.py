"""Provides user related models."""

from sqlalchemy import Column, String, Float, ForeignKey, UUID, Boolean
from sqlalchemy.orm import relationship
from khazana.core.utils import DBBaseModel
from uuid import uuid4


class UserDB(DBBaseModel):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, unique=True, index=True)
    emailAddress = Column(String, unique=True, nullable=True)
    hashed_password = Column(String)
    scopes = Column(String, default="user")
    firstLogin = Column(Boolean, default=True)
    createdBy = Column(UUID, ForeignKey("users.id"), nullable=True, default=None)
