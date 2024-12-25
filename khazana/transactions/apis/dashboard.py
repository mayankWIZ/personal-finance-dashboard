"""Transaction Dashboard related Endpoints."""

from itertools import groupby

from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func as sa_func
from sqlalchemy import or_
from sqlalchemy.orm import Session

from khazana.core.database import get_db
from khazana.core.models import UserDB
from khazana.core.utils import get_current_user

from ..models import TransactionDB
from ..utils import TransactionType

router = APIRouter(prefix="/dashboard", tags=["Transaction Dashboard"])


@router.get(
    "/{username}",
    description="Get dashboard data.",
    response_model=dict,
)
def get_dashboard_data(
    username: str,
    db: Session = Depends(get_db),
    user: UserDB = Security(
        get_current_user, scopes=["admin", "transaction_read"]
    ),
) -> dict:
    """Get aggregate data.

    For total savings, monthly expenses, and investment growth by user.
    """
    requested_user = (
        db.query(UserDB).filter(UserDB.username == username).first()
    )
    if not requested_user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = (
        db.query(
            TransactionDB.transactionDate,
            TransactionDB.amount,
        )
        .filter(
            TransactionDB.userId == requested_user.id,
            or_(
                TransactionDB.transactionType == TransactionType.income.value,
                TransactionDB.transactionType == TransactionType.expense.value,
            ),
        )
        .all()
    )
    total_savings_month_wise = {}
    for key, transactions in groupby(
        transactions,
        key=lambda x: [
            str(x.transactionDate.year),
            str(x.transactionDate.month),
        ],
    ):
        total_savings_month_wise["-".join(key)] = sum(
            transaction.amount for transaction in transactions
        )

    expenses = (
        db.query(
            TransactionDB.transactionDate,
            TransactionDB.amount,
        )
        .filter(
            TransactionDB.userId == requested_user.id,
            TransactionDB.transactionType == TransactionType.expense.value,
        )
        .all()
    )
    monthly_expenses = {}
    for key, expenses in groupby(
        expenses,
        key=lambda x: [
            str(x.transactionDate.year),
            str(x.transactionDate.month),
        ],
    ):
        monthly_expenses["-".join(key)] = sum(
            expense.amount for expense in expenses
        )
    investment_growth = (
        db.query(TransactionDB.category, sa_func.sum(TransactionDB.amount))
        .filter(
            TransactionDB.userId == requested_user.id,
            TransactionDB.transactionType == TransactionType.investment.value,
        )
        .group_by(TransactionDB.category)
        .all()
    )
    return {
        "totalSavings": total_savings_month_wise,
        "monthlyExpenses": monthly_expenses,
        "investmentGrowth": dict(investment_growth),
    }
