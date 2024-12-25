"""Transaction Dashboard serializers."""

from typing import Dict

from pydantic import BaseModel


class TransactionDashboardOut(BaseModel):
    """Transaction Dashboard out model."""

    totalSavings: Dict[str, float]
    monthlyExpenses: Dict[str, float]
    investmentGrowth: Dict[str, float]
