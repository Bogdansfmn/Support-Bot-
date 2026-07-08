"""
Модуль базы знаний
"""
import json
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """База знаний для техподдержки"""
    
    def __init__(self, base_path: str = "knowledge/base.json"):
        self.base_path = base_path
        self.knowledge = self._load_knowledge()
        logger.info(f"📚 Загружена база знаний из {base_path}")
    
    def _load_knowledge(self) -> Dict:
        """Загружает базу знаний"""
        try:
            if os.path.exists(self.base_path):
                with open(self.base_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning("База знаний не найдена, создается дефолтная")
                return self._create_default_knowledge()
        except Exception as e:
            logger.error(f"Ошибка загрузки базы знаний: {e}")
            return self._create_default_knowledge()
    
    def _create_default_knowledge(self) -> Dict:
        """Создает дефолтную базу знаний"""
        default_kb = {
            "authorization": {
                "solutions": [
                    "Пожалуйста, проверьте правильность ввода логина и пароля.",
                    "Используйте функцию 'Забыли пароль' для восстановления доступа."
                ],
                "keywords": ["логин", "пароль", "вход", "авторизация", "регистрация"]
            },
            "payment": {
                "solutions": [
                    "Проверьте статус платежа в личном кабинете.",
                    "Убедитесь, что с вашей карты списались средства."
                ],
                "keywords": ["оплата", "платеж", "карта", "деньги", "подписка"]
            },
            "bug": {
                "solutions": [
                    "Мы уже работаем над исправлением этой проблемы.",
                    "Попробуйте перезапустить приложение."
                ],
                "keywords": ["ошибка", "краш", "не работает", "баг", "сломался"]
            },
            "functionality": {
                "solutions": [
                    "Я могу помочь вам с функциональностью приложения.",
                    "Пожалуйста, уточните, что именно вы хотите сделать."
                ],
                "keywords": ["как", "где", "почему", "функция", "возможность"]
            },
            "other": {
                "solutions": ["Я понял вашу проблему. Сейчас помогу."],
                "keywords": []
            }
        }
        os.makedirs(os.path.dirname(self.base_path), exist_ok=True)
        with open(self.base_path, "w", encoding="utf-8") as f:
            json.dump(default_kb, f, ensure_ascii=False, indent=2)
        return default_kb
    
    def get_solution(self, category: str, message: str = "") -> List[str]:
        """Получает решения для категории"""
        category_data = self.knowledge.get(category, {})
        return category_data.get("solutions", ["Передаю запрос оператору."])
    
    def find_by_keywords(self, message: str) -> Optional[str]:
        """Ищет категорию по ключевым словам"""
        message_lower = message.lower()
        for category, data in self.knowledge.items():
            for keyword in data.get("keywords", []):
                if keyword.lower() in message_lower:
                    return category
        return None
