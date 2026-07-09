"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "Support Bot"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Настройки бота
    MAX_HISTORY: int = 15
    CONFIDENCE_THRESHOLD: float = 0.3
    
    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_KEY_PREFIX: str = "dialog:"
    
    # LLM
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_MODEL: str = "llama3.2:latest"
    LLM_API_KEY: str = "any_key"
    LLM_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
