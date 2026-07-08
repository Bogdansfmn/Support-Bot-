"""
Роутеры API
"""
from .webhook import router as webhook_router
from .health import router as health_router
from .history import router as history_router
from .stats import router as stats_router

__all__ = [
    "webhook_router",
    "health_router",
    "history_router",
    "stats_router"
]
