"""
Модели данных для приложения
"""
from .webhook_payload import (
    MessagePayload,
    Sender,
    Account,
    Inbox,
    Conversation,
    Attachment
)

__all__ = [
    'MessagePayload',
    'Sender',
    'Account',
    'Inbox',
    'Conversation',
    'Attachment',
]
