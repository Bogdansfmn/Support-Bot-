"""
Модели для входящих вебхуков от СпросиИИ
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Sender(BaseModel):
    """Модель отправителя"""
    id: int = Field(..., description="ID отправителя")
    name: Optional[str] = Field(None, description="Имя отправителя")
    email: Optional[str] = Field(None, description="Email отправителя")
    type: str = Field("contact", description="Тип: user/contact")


class Account(BaseModel):
    """Модель аккаунта"""
    id: int = Field(..., description="ID аккаунта")
    name: str = Field(..., description="Название аккаунта")


class Inbox(BaseModel):
    """Модель инбокса"""
    id: int = Field(..., description="ID инбокса")
    name: str = Field(..., description="Название инбокса")


class Conversation(BaseModel):
    """Модель диалога"""
    id: int = Field(..., description="ID диалога")
    display_id: Optional[int] = Field(None, description="Отображаемый ID")
    status: str = Field("open", description="Статус: open/resolved/snoozed")
    priority: Optional[str] = Field(None, description="Приоритет: low/medium/high/urgent")
    unread_count: int = Field(0, description="Количество непрочитанных")


class Attachment(BaseModel):
    """Модель вложения"""
    id: int = Field(..., description="ID вложения")
    file_url: Optional[str] = Field(None, description="URL файла")
    file_type: Optional[str] = Field(None, description="Тип файла")
    thumb_url: Optional[str] = Field(None, description="URL миниатюры")


class MessagePayload(BaseModel):
    """
    Модель входящего вебхука message_created от СпросиИИ
    """
    event: str = Field(..., description="Тип события (message_created)")
    id: int = Field(..., description="ID сообщения")
    content: str = Field(..., description="Текст сообщения")
    content_type: str = Field("text", description="Тип контента")
    content_attributes: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные атрибуты")
    message_type: str = Field(..., description="Тип: incoming/outgoing")
    created_at: Optional[datetime] = Field(None, description="Дата создания")
    private: bool = Field(False, description="Приватное сообщение")
    source_id: Optional[str] = Field(None, description="Внешний ID")
    sender: Sender = Field(..., description="Отправитель")
    account: Account = Field(..., description="Аккаунт")
    conversation: Conversation = Field(..., description="Диалог")
    inbox: Inbox = Field(..., description="Инбокс")
    additional_attributes: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные атрибуты")
    attachments: List[Attachment] = Field(default_factory=list, description="Вложения")

    class Config:
        json_schema_extra = {
            "example": {
                "event": "message_created",
                "id": 123,
                "content": "Не могу войти в аккаунт",
                "content_type": "text",
                "message_type": "incoming",
                "private": False,
                "sender": {
                    "id": 456,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "type": "contact"
                },
                "account": {"id": 1, "name": "My Account"},
                "conversation": {"id": 789, "display_id": 456, "status": "open"},
                "inbox": {"id": 10, "name": "Support"},
                "attachments": []
            }
        }
