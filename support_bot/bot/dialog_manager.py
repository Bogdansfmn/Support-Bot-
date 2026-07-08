"""
Модуль управления историей диалогов
"""
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging
from config import settings

# Пытаемся импортировать redis, если он установлен
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class DialogManager:
    """Менеджер истории диалогов с поддержкой Redis"""
    
    def __init__(self, max_history: int = 15):
        self.max_history = max_history
        self._redis_client = None
        self._memory_history = {}  # Fallback: храним в памяти
        self._init_redis()
    
    def _init_redis(self):
        """Инициализация Redis клиента"""
        if not REDIS_AVAILABLE:
            logger.warning("⚠️ Redis не установлен, используем память")
            return
        
        try:
            if settings.REDIS_URL:
                self._redis_client = redis.from_url(settings.REDIS_URL)
                self._redis_client.ping()
                logger.info("✅ Redis подключен")
        except Exception as e:
            logger.warning(f"⚠️ Redis не доступен: {e}, используем память")
            self._redis_client = None
    
    def _get_redis_key(self, user_id: str) -> str:
        """Получает ключ для Redis"""
        return f"{settings.REDIS_KEY_PREFIX}{user_id}"
    
    def add_message(self, user_id: str, message: str, role: str = "user") -> None:
        """Добавляет сообщение в историю"""
        msg_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "role": role
        }
        
        # Сохраняем в Redis
        if self._redis_client:
            try:
                key = self._get_redis_key(user_id)
                self._redis_client.rpush(key, json.dumps(msg_data))
                self._redis_client.ltrim(key, -self.max_history, -1)
                self._redis_client.expire(key, 86400 * 7)  # 7 дней
                return
            except Exception as e:
                logger.warning(f"⚠️ Ошибка Redis: {e}, используем память")
        
        # Fallback: храним в памяти
        if user_id not in self._memory_history:
            self._memory_history[user_id] = []
        self._memory_history[user_id].append(msg_data)
        if len(self._memory_history[user_id]) > self.max_history:
            self._memory_history[user_id] = self._memory_history[user_id][-self.max_history:]
    
    def get_history(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Получает историю диалога"""
        # Пытаемся получить из Redis
        if self._redis_client:
            try:
                key = self._get_redis_key(user_id)
                if limit:
                    data = self._redis_client.lrange(key, -limit, -1)
                else:
                    data = self._redis_client.lrange(key, 0, -1)
                if data:
                    return [json.loads(msg.decode()) for msg in data]
            except Exception as e:
                logger.warning(f"⚠️ Ошибка Redis: {e}, используем память")
        
        # Fallback: из памяти
        if user_id in self._memory_history:
            history = self._memory_history[user_id]
            if limit:
                return history[-limit:]
            return history
        return []
    
    def get_context_summary(self, user_id: str) -> str:
        """Создает краткую сводку контекста"""
        history = self.get_history(user_id, limit=5)
        if not history:
            return ""
        user_messages = [msg["message"] for msg in history if msg["role"] == "user"]
        return " ".join(user_messages)
    
    def add_response(self, user_id: str, message: str) -> None:
        """Добавляет ответ бота в историю"""
        self.add_message(user_id, message, role="assistant")
    
    def clear_history(self, user_id: str) -> None:
        """Очищает историю пользователя"""
        if self._redis_client:
            try:
                self._redis_client.delete(self._get_redis_key(user_id))
            except Exception as e:
                logger.warning(f"⚠️ Ошибка Redis: {e}")
        self._memory_history.pop(user_id, None)
    
    def get_stats(self) -> Dict:
        """Получает статистику"""
        if self._redis_client:
            try:
                pattern = f"{settings.REDIS_KEY_PREFIX}*"
                keys = self._redis_client.keys(pattern)
                total_users = len(keys)
                total_messages = sum(self._redis_client.llen(key) for key in keys)
                return {
                    "total_users": total_users,
                    "total_messages": total_messages,
                    "max_history": self.max_history,
                    "storage": "redis"
                }
            except Exception as e:
                logger.warning(f"⚠️ Ошибка Redis: {e}")
        
        return {
            "total_users": len(self._memory_history),
            "total_messages": sum(len(msgs) for msgs in self._memory_history.values()),
            "max_history": self.max_history,
            "storage": "memory"
        }
