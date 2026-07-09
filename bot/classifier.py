"""
Модуль классификации обращений
"""
from typing import Dict, Tuple, List
from datetime import datetime
from bot.dialog_manager import DialogManager
from bot.knowledge_base import KnowledgeBase
import logging

logger = logging.getLogger(__name__)


class SupportClassifier:
    """Классификатор обращений в техподдержку"""
    
    def __init__(self, dialog_manager: DialogManager):
        self.dialog_manager = dialog_manager
        self.knowledge_base = KnowledgeBase()
        self._init_rules()
    
    def _init_rules(self):
        """Инициализация правил классификации"""
        self.category_rules = {
            "authorization": {
                "keywords": ["логин", "пароль", "авториз", "вход", "регистрац", "аккаунт", "войти"],
                "priority": "high"
            },
            "payment": {
                "keywords": ["оплат", "платеж", "карт", "счет", "биллинг", "деньги", "подписк"],
                "priority": "high"
            },
            "bug": {
                "keywords": ["ошибка", "краш", "вылет", "не работает", "баг", "сломал", "завис"],
                "priority": "high"
            },
            "functionality": {
                "keywords": ["как", "где", "почему", "функция", "возможн", "работает", "настро"],
                "priority": "medium"
            }
        }
        self.critical_keywords = ["срочно", "критично", "немедленно", "очень важно"]
    
    def classify(self, user_id: str, message: str) -> Dict:
        """Классифицирует обращение пользователя"""
        logger.info(f"🔍 Классификация обращения от {user_id}")
        
        history = self.dialog_manager.get_history(user_id)
        context = self.dialog_manager.get_context_summary(user_id)
        
        category, confidence = self._detect_category(message.lower(), context)
        priority = self._calculate_priority(category, message, history)
        solution = self._get_solution(category, message)
        escalate = self._check_escalation(priority, history, category)
        
        result = {
            "category": category,
            "priority": priority,
            "confidence": round(confidence, 2),
            "solution": solution,
            "escalate_to_human": escalate,
            "tags": [category, priority],
            "timestamp": datetime.now().isoformat(),
            "needs_clarification": confidence < 0.3
        }
        
        if escalate:
            result["operator_context"] = {
                "summary": f"Пользователь обратился с проблемой в категории {category}",
                "priority": priority,
                "history": history[-5:] if history else [],
                "reason": "Требуется вмешательство оператора"
            }
        
        logger.info(f"📊 Результат: {result['category']}, приоритет: {result['priority']}")
        return result
    
    def _detect_category(self, text: str, context: str) -> Tuple[str, float]:
        """Определяет категорию обращения"""
        kb_category = self.knowledge_base.find_by_keywords(text)
        if kb_category:
            return kb_category, 0.85
        
        best_score = 0
        best_cat = "other"
        
        for category, rules in self.category_rules.items():
            score = sum(1 for keyword in rules["keywords"] if keyword in text)
            if context:
                score += sum(0.5 for keyword in rules["keywords"] if keyword in context)
            if score > best_score:
                best_score = score
                best_cat = category
        
        max_keywords = max(len(rules["keywords"]) for rules in self.category_rules.values())
        confidence = min(0.95, best_score / max_keywords) if best_score > 0 else 0.1
        return best_cat, confidence
    
    def _calculate_priority(self, category: str, text: str, history: List) -> str:
        """Рассчитывает приоритет"""
        if any(word in text.lower() for word in self.critical_keywords):
            return "critical"
        if category in self.category_rules:
            return self.category_rules[category]["priority"]
        if len(history) > 3:
            return "high"
        return "medium"
    
    def _get_solution(self, category: str, message: str) -> str:
        """Получает решение из базы знаний"""
        solutions = self.knowledge_base.get_solution(category, message)
        return solutions[0] if solutions else "Я понял вашу проблему. Сейчас помогу."
    
    def _check_escalation(self, priority: str, history: List, category: str) -> bool:
        """Проверяет необходимость эскалации"""
        if priority in ["critical", "high"] and len(history) >= 3:
            return True
        if category == "other" and len(history) >= 4:
            return True
        return False
