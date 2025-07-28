"""
Сервис для работы с знаниями пользователей
"""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import UserKnowledgeRecord
from app.schemas import UserKnowledge

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Сервис для работы с знаниями пользователей"""
    
    def __init__(self):
        self.knowledge_base_path = Path(settings.knowledge_base_path)
        self._cache = {}  # Простой кэш в памяти
    
    async def load_user_knowledge(self, user_id: str, db: AsyncSession) -> Optional[UserKnowledge]:
        """
        Загружает знания пользователя из JSON файла или БД
        
        Args:
            user_id: ID пользователя
            db: Сессия базы данных
            
        Returns:
            Знания пользователя или None
        """
        # Проверяем кэш
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Пытаемся загрузить из БД
        knowledge = await self._load_from_database(user_id, db)
        if knowledge:
            self._cache[user_id] = knowledge
            return knowledge
        
        # Загружаем из JSON файла
        knowledge = await self._load_from_json_file(user_id)
        if knowledge:
            # Сохраняем в БД для будущего использования
            await self._save_to_database(knowledge, db)
            self._cache[user_id] = knowledge
            return knowledge
        
        logger.warning(f"Knowledge not found for user {user_id}")
        return None
    
    async def _load_from_database(self, user_id: str, db: AsyncSession) -> Optional[UserKnowledge]:
        """Загружает знания из базы данных"""
        try:
            result = await db.execute(
                select(UserKnowledgeRecord).where(UserKnowledgeRecord.user_id == user_id)
            )
            record = result.scalar_one_or_none()
            
            if record:
                return UserKnowledge(
                    user_id=record.user_id,
                    name=record.name,
                    personality=record.personality,
                    background=record.background,
                    expertise=record.expertise,
                    communication_style=record.communication_style,
                    preferences=record.preferences,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
        
        return None
    
    async def _load_from_json_file(self, user_id: str) -> Optional[UserKnowledge]:
        """Загружает знания из JSON файла"""
        file_path = self.knowledge_base_path / f"{user_id}.json"
        
        if not file_path.exists():
            logger.info(f"JSON file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return UserKnowledge(**data)
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return None
    
    async def _save_to_database(self, knowledge: UserKnowledge, db: AsyncSession):
        """Сохраняет знания в базу данных"""
        try:
            # Проверяем, существует ли запись
            result = await db.execute(
                select(UserKnowledgeRecord).where(
                    UserKnowledgeRecord.user_id == knowledge.user_id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Обновляем существующую запись
                existing.name = knowledge.name
                existing.personality = knowledge.personality
                existing.background = knowledge.background
                existing.expertise = knowledge.expertise
                existing.communication_style = knowledge.communication_style
                existing.preferences = knowledge.preferences
            else:
                # Создаем новую запись
                record = UserKnowledgeRecord(
                    user_id=knowledge.user_id,
                    name=knowledge.name,
                    personality=knowledge.personality,
                    background=knowledge.background,
                    expertise=knowledge.expertise,
                    communication_style=knowledge.communication_style,
                    preferences=knowledge.preferences,
                    file_path=str(self.knowledge_base_path / f"{knowledge.user_id}.json")
                )
                db.add(record)
            
            await db.commit()
            logger.info(f"Saved knowledge for user {knowledge.user_id} to database")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            await db.rollback()
    
    async def get_all_user_ids(self) -> List[str]:
        """Возвращает список всех доступных пользователей"""
        user_ids = []
        
        # Сканируем JSON файлы
        if self.knowledge_base_path.exists():
            for file_path in self.knowledge_base_path.glob("*.json"):
                user_id = file_path.stem
                user_ids.append(user_id)
        
        return user_ids
    
    def clear_cache(self):
        """Очищает кэш"""
        self._cache.clear()
    
    async def create_character_prompt(
        self, 
        user_knowledge: UserKnowledge, 
        question: str,
        context_docs: List[Dict[str, Any]],
        reply_to: Optional[str] = None
    ) -> str:
        """
        Создает промпт для генерации ответа от имени пользователя
        
        Args:
            user_knowledge: Знания пользователя
            question: Вопрос
            context_docs: Контекстные документы
            reply_to: Кому адресован ответ
            
        Returns:
            Сгенерированный промпт
        """
        # Формируем контекст из найденных документов
        context_text = "\n\n".join([
            f"Документ {i+1} (similarity: {doc.get('similarity_score', 0):.3f}):\n{doc.get('content', '')}"
            for i, doc in enumerate(context_docs[:5])  # Берем топ-5
        ])
        
        # Формируем информацию о целевом пользователе
        reply_context = ""
        if reply_to:
            reply_context = f"\n\nТы отвечаешь пользователю: {reply_to}"
        
        # Создаем промпт
        prompt = f"""Ты - {user_knowledge.name} ({user_knowledge.user_id}).

ТВОЯ ЛИЧНОСТЬ И ХАРАКТЕР:
{user_knowledge.personality}

ТВОЙ БЭКГРАУНД:
{user_knowledge.background}

ТВОЯ ЭКСПЕРТИЗА:
{', '.join(user_knowledge.expertise)}

ТВОЙ СТИЛЬ ОБЩЕНИЯ:
{user_knowledge.communication_style}

ТВОИ ПРЕДПОЧТЕНИЯ:
- Длина ответа: {user_knowledge.preferences.get('response_length', 'medium')}
- Включать примеры кода: {user_knowledge.preferences.get('include_code_examples', False)}
- Ссылаться на источники: {user_knowledge.preferences.get('cite_sources', False)}
- Технический уровень: {user_knowledge.preferences.get('technical_level', 'intermediate')}

РЕЛЕВАНТНЫЙ КОНТЕКСТ ИЗ ПРЕДЫДУЩИХ ОБСУЖДЕНИЙ:
{context_text if context_text.strip() else "Контекст не найден - отвечай на основе своих знаний."}

ВОПРОС:
{question}{reply_context}

ИНСТРУКЦИЯ:
Ответь на вопрос как {user_knowledge.name}, используя свою личность, стиль общения и экспертизу. 
Опирайся на предоставленный контекст, но если он недостаточен, используй свои знания в области твоей экспертизы.
Сохраняй характерный для тебя стиль и манеру изложения.
"""
        
        return prompt.strip()
