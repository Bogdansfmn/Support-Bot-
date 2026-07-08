"""
Обработчик вебхуков от СпросиИИ
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import logging

from models.webhook_payload import MessagePayload
from bot.classifier import SupportClassifier
from bot.dialog_manager import DialogManager
from bot.responses import ResponseManager
from config import settings

router = APIRouter(prefix="/webhook", tags=["Webhook"])
logger = logging.getLogger(__name__)

# Инициализация компонентов
dialog_manager = DialogManager(max_history=settings.MAX_HISTORY)
classifier = SupportClassifier(dialog_manager)
response_manager = ResponseManager()

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Обработка входящего вебхука"
)
async def process_webhook(payload: MessagePayload) -> Dict[str, Any]:
    """Обработка входящего вебхука от СпросиИИ"""
    try:
        logger.info(f"📨 Получен вебхук: {payload.event}")
        
        if payload.event != "message_created":
            return {"status": "ignored", "reason": "not_message_created"}
        
        if payload.message_type != "incoming":
            return {"status": "ignored", "reason": "not_incoming"}
        
        if payload.private:
            return {"status": "ignored", "reason": "private_message"}
        
        user_id = str(payload.sender.id)
        dialog_manager.add_message(user_id, payload.content)
        
        result = classifier.classify(user_id, payload.content)
        
        if result["needs_clarification"]:
            reply = response_manager.get_response("clarification")
        elif result["escalate_to_human"]:
            reply = response_manager.get_response("escalation")
        else:
            reply = result["solution"]
        
        dialog_manager.add_response(user_id, reply)
        
        return {
            "status": "processed",
            "conversation_id": payload.conversation.id,
            "reply": {
                "content": reply,
                "message_type": "outgoing",
                "private": False,
                "content_type": "text",
                "content_attributes": {}
            },
            "metadata": {
                "category": result["category"],
                "priority": result["priority"],
                "confidence": result["confidence"],
                "needs_escalation": result["escalate_to_human"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка: {str(e)}"
        )
