"""
Модели для ответов API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ReplyContent(BaseModel):
    """Содержимое ответа"""
    content: str = Field(..., description="Текст ответа")
    message_type: str = Field("outgoing", description="Тип сообщения")
    private: bool = Field(False, description="Приватное сообщение")
    content_type: str = Field("text", description="Тип контента")
    content_attributes: Dict[str, Any] = Field(default_factory=dict)

class WebhookResponse(BaseModel):
    """Ответ на вебхук"""
    status: str = Field(..., description="Статус обработки")
    conversation_id: int = Field(..., description="ID диалога")
    reply: ReplyContent = Field(..., description="Ответ бота")
    metadata: Dict[str, Any] = Field(..., description="Метаданные классификации")
