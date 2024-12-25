"""Constants."""

from enum import Enum


class TransactionType(str, Enum):
    """Transaction Types."""

    expense = "expense"
    income = "income"
    investment = "investment"
