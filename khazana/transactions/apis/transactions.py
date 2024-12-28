"""Transaction related Endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from khazana.core.database import get_db
from khazana.core.models import UserDB
from khazana.core.utils import get_current_user

from ..models import TransactionDB
from ..serializers import TransactionIn, TransactionOut, TransactionUpdate
from ..utils import TransactionType

router = APIRouter(tags=["Transactions"])


@router.get(
    "",
    description="Get list of transactions.",
    response_model=List[TransactionOut],
)
def list_transactions(
    db: Session = Depends(get_db),
    user: UserDB = Security(get_current_user, scopes=["transaction_read"]),
) -> List[TransactionOut]:
    """List transactions."""
    return (
        db.query(TransactionDB).filter(TransactionDB.userId == user.id).all()
    )


@router.get(
    "/{username}",
    description="Get list of transactions.",
    response_model=List[TransactionOut],
)
def list_user_transactions(
    username: str,
    db: Session = Depends(get_db),
    user: UserDB = Security(
        get_current_user, scopes=["admin", "transaction_read"]
    ),
) -> List[TransactionOut]:
    """List transactions by user."""
    requested_user = (
        db.query(UserDB).filter(UserDB.username == username, UserDB.active == True).first()
    )
    if not requested_user:
        raise HTTPException(status_code=404, detail="User not found")
    return (
        db.query(TransactionDB)
        .filter(TransactionDB.userId == requested_user.id)
        .all()
    )


@router.post(
    "",
    description="Create a transaction.",
    response_model=TransactionOut,
)
def create_transaction(
    transaction: TransactionIn,
    db: Session = Depends(get_db),
    user: UserDB = Security(get_current_user, scopes=["transaction_write"]),
) -> TransactionOut:
    """Create a user transaction."""
    transaction_type = transaction.transactionType
    if (
        transaction.amount < 0
        and transaction_type != TransactionType.investment
    ):
        transaction_type = TransactionType.expense
    elif (
        transaction.amount > 0
        and transaction_type != TransactionType.investment
    ):
        transaction_type = TransactionType.income
    transaction = TransactionDB(
        **{
            **transaction.model_dump(),
            "userId": user.id,
            "createdBy": user.id,
            "transactionType": transaction_type,
        }
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.patch(
    "/{transaction_id}",
    description="Update a transaction.",
    response_model=TransactionOut,
)
def update_transaction(
    transaction_id: UUID,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    user: UserDB = Security(get_current_user, scopes=["transaction_write"]),
):
    """Update a transaction."""
    transaction = (
        db.query(TransactionDB)
        .filter(
            TransactionDB.id == transaction_id, TransactionDB.userId == user.id
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    updates = transaction_update.model_dump(
        exclude_none=True, exclude_unset=True
    )
    if not updates:
        raise HTTPException(
            status_code=400, detail="No fields to update provided"
        )
    for key, value in updates.items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return TransactionOut(**transaction.__dict__)


@router.delete(
    "/{transaction_id}",
    description="Delete a transaction.",
)
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    user: UserDB = Security(get_current_user, scopes=["transaction_write"]),
):
    """Delete a transaction."""
    transaction = (
        db.query(TransactionDB)
        .filter(
            TransactionDB.id == transaction_id, TransactionDB.userId == user.id
        )
        .first()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()
    return {"success": True}
