"""Exchange Rate routers."""
from .transactions import router as transactions_router

routers = [
    transactions_router
]
