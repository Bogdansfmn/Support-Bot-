"""
Проверка состояния сервиса
"""
from fastapi import APIRouter
from datetime import datetime
from config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat()
    }
