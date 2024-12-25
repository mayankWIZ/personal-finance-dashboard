from sqlalchemy import Column, UUID, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from khazana.core.utils import DBBaseModel
from uuid import uuid4
from datetime import datetime, timezone
from ..utils import TransactionType


class TransactionDB(DBBaseModel):
    __tablename__ = "transactions"
    id = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    userId = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    description = Column(String)
    amount = Column(Float, nullable=False, default=0.0)
    category = Column(String, nullable=False, index=True)
    transactionDate = Column(
        DateTime, default=datetime.now(timezone.utc), index=True
    )
    createdBy = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    transactionType = Column(
        String,
        nullable=False,
        default=TransactionType.expense.value,
        index=True,
    )

    user = relationship(
        "UserDB",
        back_populates="transactions",
        foreign_keys="TransactionDB.userId"
    )
