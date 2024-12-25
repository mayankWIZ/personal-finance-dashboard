"""Constants."""
from enum import Enum


class TransactionType(str, Enum):
    expense = "expense"
    income = "income"
    investment = "investment"
