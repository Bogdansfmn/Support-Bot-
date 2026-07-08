"""
Управление историей диалогов
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from bot.dialog_manager import DialogManager
from config import settings

router = APIRouter(prefix="/history", tags=["History"])
dialog_manager = DialogManager(max_history=settings.MAX_HISTORY)

@router.get("/{user_id}")
async def get_history(user_id: str, limit: Optional[int] = 10):
    try:
        history = dialog_manager.get_history(user_id, limit=limit)
        return {
            "user_id": user_id,
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка: {str(e)}"
        )

@router.delete("/{user_id}")
async def clear_history(user_id: str):
    try:
        dialog_manager.clear_history(user_id)
        return {"status": "success", "message": f"История для {user_id} очищена"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка: {str(e)}"
        )
