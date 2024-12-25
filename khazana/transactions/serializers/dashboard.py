"""Transaction Dashboard serializers."""

from pydantic import BaseModel
from typing import Dict


class TransactionDashboardOut(BaseModel):
    """Transaction Dashboard out model."""

    totalSavings: Dict[str, float]
    monthlyExpenses: Dict[str, float]
    investmentGrowth: Dict[str, float]
