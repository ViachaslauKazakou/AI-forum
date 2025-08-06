"""
Конфигурация приложения
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class ForumSettings(BaseSettings):
    """Настройки приложения"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://docker:docker@localhost:5433/postgres")
    
    # AI Manager
    AI_MANAGER_URL: str = os.getenv("AI_MANAGER_URL", "http://localhost:8080")
    AI_MANAGER_API_KEY: Optional[str] = os.getenv("AI_MANAGER_API_KEY", "your-ai-manager-api-key-here")
    
    # RAG Service
    RAG_MANAGER_URL: Optional[str] = os.getenv("RAG_MANAGER_URL")
    RAG_SERVICE_API_KEY: Optional[str] = os.getenv("RAG_SERVICE_API_KEY")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Ollama
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # Paths
    # knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "./forum_knowledge_base")

    # # API Settings
    # api_title: str = "RAG Manager API"
    # api_version: str = "1.0.0"
    # api_description: str = "RAG Manager Service for AI Forum"

    # # Vector DB Settings
    # embedding_dimension: int = 1536  # OpenAI ada-002

    # # Performance
    # max_context_documents: int = 20
    # default_similarity_threshold: float = 0.7
    # cache_ttl: int = 300  # 5 minutes

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Игнорировать дополнительные поля из .env


# Глобальный экземпляр настроек
get_settings = ForumSettings()
