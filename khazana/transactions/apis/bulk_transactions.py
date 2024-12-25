"""Bulk transactions related Endpoints."""

import os
import tempfile
from datetime import datetime, timezone

import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Security,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from khazana.core.database import get_db
from khazana.core.models import UserDB
from khazana.core.utils import get_current_user

from ..models import TransactionDB
from ..serializers import TransactionOut
from ..utils import TransactionType

router = APIRouter(prefix="/bulk", tags=["Bulk Transactions"])


def _select_transaction_type(record):
    if not record["transactionType"]:
        transaction_type = TransactionType.expense.value
    else:
        transaction_type = record["transactionType"].lower()
    transaction_type = TransactionType(transaction_type).value
    if (
        record["amount"] < 0
        and transaction_type != TransactionType.investment.value
    ):
        transaction_type = TransactionType.expense.value
    elif (
        record["amount"] > 0
        and transaction_type != TransactionType.investment.value
    ):
        transaction_type = TransactionType.income.value
    return transaction_type


@router.post(
    "/{username}",
    description="Create bulk transactions.",
    # response_model=List[TransactionOut],
)
def create_bulk_transactions(
    username: str,
    transaction_file: UploadFile = File(
        ..., description="CSV file of transactions"
    ),
    db: Session = Depends(get_db),
    user: UserDB = Security(
        get_current_user, scopes=["admin", "transaction_write"]
    ),
):
    """Create bulk transactions."""
    transaction_user = (
        db.query(UserDB).filter(UserDB.username == username).first()
    )
    if not transaction_user:
        raise HTTPException(status_code=404, detail="User not found")

    filename = transaction_file.filename
    ext = os.path.splitext(filename)[1]
    if ext.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Invalid file format")

    print(f"Importing transactions from {filename}...")
    transactions = pd.read_csv(transaction_file.file)
    transactions["userId"] = transaction_user.id
    transactions["createdBy"] = user.id

    transactions["category"] = transactions["category"].fillna("Uncategorized")
    transactions["category"] = transactions["category"].replace(
        {"": "Uncategorized", None: "Uncategorized"}
    )

    # Check is transactionDate is having na/none values
    if transactions["transactionDate"].isna().any():
        raise HTTPException(
            status_code=400,
            detail="Transaction date can not be null or in the future",
        )

    # Convert transactionDate to datetime
    transactions["transactionDate"] = pd.to_datetime(
        transactions["transactionDate"], utc=True
    )

    # Validate transactionDate is not in the future
    if transactions["transactionDate"].max() > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Transaction date can not be in the future",
        )

    # Logic to select transactionType based on amount
    transactions["transactionType"] = transactions.apply(
        _select_transaction_type, axis=1
    )

    transactions = transactions.to_dict(orient="records")
    db.bulk_insert_mappings(TransactionDB, transactions)
    db.commit()
    return {"success": True}


@router.get(
    "/{username}",
    description="Export user transactions.",
)
def export_transactions(
    username: str,
    db: Session = Depends(get_db),
    user: UserDB = Security(
        get_current_user, scopes=["admin", "transaction_read"]
    ),
):
    """Export user transactions."""
    requested_user = (
        db.query(UserDB).filter(UserDB.username == username).first()
    )
    if not requested_user:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = (
        db.query(TransactionDB)
        .filter(TransactionDB.userId == requested_user.id)
        .all()
    )
    if not transactions:
        raise HTTPException(
            status_code=400, detail="No transactions to export"
        )
    with tempfile.NamedTemporaryFile() as temp_file:
        pd.DataFrame(
            [
                TransactionOut(**transaction.__dict__).model_dump()
                for transaction in transactions
            ]
        ).to_csv(temp_file.name, index=False)
        dnow = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return StreamingResponse(
            iter([temp_file.read()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    f"attachment; filename={username}_"
                    f"transactions_"
                    f"{dnow}.csv"
                )
            },
        )
