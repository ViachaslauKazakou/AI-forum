"""
Pydantic модели для RAG Manager
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RAGRequest(BaseModel):
    """Запрос для обработки RAG"""
    topic: str = Field(..., description="Топик обсуждения")
    user_id: str = Field(..., description="ID пользователя от имени которого ответ")
    question: str = Field(..., description="Вопрос для обработки")
    reply_to: Optional[str] = Field(None, description="ID пользователя, кому ответ")
    context_limit: Optional[int] = Field(10, description="Лимит контекстных документов")
    similarity_threshold: Optional[float] = Field(0.7, description="Порог схожести для поиска")


class ContextItem(BaseModel):
    """
    Элемент контекста
    """
    content: str = Field(..., description="Содержимое контекста")
    source: str = Field(..., description="Источник контекста")
    similarity_score: float = Field(..., description="Оценка схожести")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Дополнительные метаданные")


class RAGResponse(BaseModel):
    """Ответ от RAG системы"""
    enhanced_prompt: str = Field(..., description="Сгенерированный промпт")
    context_items: List[ContextItem] = Field(..., description="Найденные элементы контекста")
    user_persona: Dict[str, Any] = Field(..., description="Персона пользователя")
    processing_time: float = Field(..., description="Время обработки в секундах")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время обработки")


class UserKnowledge(BaseModel):
    """Знания пользователя"""
    user_id: str
    name: str
    personality: str
    background: str
    expertise: List[str]
    communication_style: str
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ContextDocument(BaseModel):
    """Контекстный документ из векторной БД"""
    id: int
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    topic_id: Optional[int] = None
    message_id: Optional[int] = None


class HealthStatus(BaseModel):
    """Статус здоровья сервиса"""
    status: str
    timestamp: datetime
    database_status: str
    vector_db_status: str
    knowledge_base_status: str
    uptime: float
