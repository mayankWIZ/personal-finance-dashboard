"""Transaction routers."""
from .transactions import router as transactions_router
from .bulk_transactions import router as bulk_transactions_router
from .dashboard import router as dashboard_router

routers = [
    dashboard_router,
    transactions_router,
    bulk_transactions_router,
]
