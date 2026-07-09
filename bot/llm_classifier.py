"""
Классификатор с использованием LLM для анализа и генерации ответов
"""
from typing import Dict, List
from datetime import datetime
import logging
from bot.dialog_manager import DialogManager
from bot.knowledge_base import KnowledgeBase
from bot.llm_client import LLMClient

logger = logging.getLogger(__name__)


class LLMClassifier:
    """Классификатор с использованием языковой модели"""
    
    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.knowledge_base = KnowledgeBase()
        self.llm = LLMClient()
    
    def classify(self, user_id: str, message: str) -> Dict:
        """
        Классифицирует обращение и генерирует ответ с помощью LLM
        """
        logger.info(f"🤖 LLM-обработка обращения от {user_id}")
        
        # Получаем историю и контекст
        history = self.dialog_manager.get_history(user_id)
        context = self.dialog_manager.get_context_summary(user_id)
        
        # Определяем категорию и приоритет (используем базовый классификатор)
        category, priority = self._quick_classify(message, context)
        
        # Генерируем ответ через LLM
        answer = self.llm.generate_response(
            message=message,
            context=context,
            category=category,
            priority=priority
        )
        
        # Проверяем необходимость эскалации
        escalate = self._check_escalation(priority, history, category)
        
        result = {
            "category": category,
            "priority": priority,
            "confidence": 0.85 if category != "other" else 0.4,
            "solution": answer,
            "escalate_to_human": escalate,
            "tags": [category, priority],
            "timestamp": datetime.now().isoformat(),
            "needs_clarification": False,
            "llm_used": True,
            "model": self.llm.model
        }
        
        if escalate:
            result["operator_context"] = {
                "summary": f"Пользователь обратился с проблемой в категории {category}",
                "priority": priority,
                "history": history[-5:] if history else [],
                "reason": "Требуется вмешательство оператора"
            }
        
        logger.info(f"📊 LLM результат: {result['category']}, приоритет: {result['priority']}")
        return result
    
    def _quick_classify(self, message: str, context: str) -> tuple:
        """Быстрая классификация на основе ключевых слов"""
        text = message.lower()
        
        categories = {
            "authorization": ["логин", "пароль", "войти", "вход", "авторизация", "регистрация", "аккаунт"],
            "payment": ["оплата", "платеж", "карта", "деньги", "подписка", "биллинг"],
            "bug": ["ошибка", "краш", "не работает", "баг", "сломался", "вылет"],
            "functionality": ["как", "где", "почему", "функция", "возможность", "настроить"]
        }
        
        best_score = 0
        best_cat = "other"
        
        for cat, keywords in categories.items():
            score = sum(1 for word in keywords if word in text)
            if score > best_score:
                best_score = score
                best_cat = cat
        
        # Определяем приоритет
        critical_keywords = ["срочно", "критично", "немедленно", "очень важно", "авария"]
        if any(word in text for word in critical_keywords):
            priority = "critical"
        elif best_cat in ["authorization", "payment", "bug"]:
            priority = "high"
        elif best_cat == "functionality":
            priority = "medium"
        else:
            priority = "low"
        
        return best_cat, priority
    
    def _check_escalation(self, priority: str, history: List, category: str) -> bool:
        """Проверяет необходимость эскалации"""
        if priority in ["critical", "high"] and len(history) >= 3:
            return True
        if category == "other" and len(history) >= 4:
            return True
        return False