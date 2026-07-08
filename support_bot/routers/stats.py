"""
Статистика сервиса
"""
from fastapi import APIRouter
from bot.dialog_manager import DialogManager
from config import settings

router = APIRouter(prefix="/stats", tags=["Stats"])
dialog_manager = DialogManager(max_history=settings.MAX_HISTORY)

@router.get("/")
async def get_stats():
    return dialog_manager.get_stats()
