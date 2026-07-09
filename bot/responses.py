"""
Модуль управления ответами бота
"""
import random
import logging

logger = logging.getLogger(__name__)

class ResponseManager:
    """Менеджер ответов бота"""
    
    def __init__(self):
        self.responses = {
            "greeting": [
                "Здравствуйте! Чем я могу вам помочь?",
                "Привет! Задавайте ваш вопрос."
            ],
            "clarification": [
                "Пожалуйста, уточните ваш вопрос.",
                "Можете описать проблему подробнее?"
            ],
            "escalation": [
                "Я передаю ваш запрос оператору. Ожидайте, пожалуйста.",
                "Сейчас вас соединит с оператором."
            ],
            "default": ["Я понял ваш запрос. Сейчас помогу."]
        }
    
    def get_response(self, key: str, fallback: str = "default") -> str:
        """Получает случайный ответ из категории"""
        responses = self.responses.get(key, self.responses.get(fallback, ["Я понял ваш запрос."]))
        return random.choice(responses)
