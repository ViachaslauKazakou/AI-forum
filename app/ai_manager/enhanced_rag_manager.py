"""
Улучшенный RAG Manager с поддержкой очередей и кэширования
"""
import asyncio
import json
from typing import Any, Dict, List, Optional

import redis
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.embedding_manager import EmbeddingManager


class EnhancedRAGManager:
    """Улучшенный RAG Manager с очередями и кэшированием"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)
        self.embedding_manager = EmbeddingManager()
        self.celery_app = Celery('rag_manager')
        
    async def process_character_request(
        self, 
        character_name: str, 
        user_query: str,
        context_window: int = 5000
    ) -> Dict[str, Any]:
        """
        Обработка запроса с учетом персонажа
        
        Args:
            character_name: Имя персонажа для RAG
            user_query: Запрос пользователя
            context_window: Размер контекстного окна
            
        Returns:
            Сформированный промпт и метаданные
        """
        
        # 1. Проверяем кэш
        cache_key = f"character:{character_name}:query:{hash(user_query)}"
        cached_result = self.redis_client.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # 2. Получаем эмбеддинг запроса
        query_embedding = await self._get_query_embedding(user_query)
        
        # 3. Ищем релевантные документы персонажа
        relevant_docs = await self._search_character_knowledge(
            character_name, 
            query_embedding,
            limit=10
        )
        
        # 4. Формируем контекст
        context = await self._build_context(
            relevant_docs, 
            context_window
        )
        
        # 5. Создаем промпт
        prompt = await self._create_character_prompt(
            character_name,
            user_query,
            context
        )
        
        result = {
            "prompt": prompt,
            "character": character_name,
            "context_docs": len(relevant_docs),
            "confidence": self._calculate_confidence(relevant_docs)
        }
        
        # 6. Кэшируем результат
        self.redis_client.setex(
            cache_key, 
            300,  # 5 минут
            json.dumps(result)
        )
        
        return result
    
    async def _search_character_knowledge(
        self, 
        character_name: str, 
        query_embedding: List[float],
        limit: int = 10
    ) -> List[Dict]:
        """Поиск знаний персонажа в векторной БД"""
        
        results = await self.embedding_manager.search_similar_messages(
            query_embedding=query_embedding,
            limit=limit,
            similarity_threshold=0.7
        )
        
        # Фильтруем по персонажу
        character_results = []
        for result in results:
            metadata = result[5]  # metadata из результата
            if metadata.get('character') == character_name:
                character_results.append({
                    'content': result[3],
                    'similarity': result[4],
                    'metadata': metadata
                })
        
        return character_results
    
    async def _create_character_prompt(
        self,
        character_name: str,
        user_query: str,
        context: str
    ) -> str:
        """Создание промпта с учетом персонажа"""
        
        # Загружаем базовую личность персонажа
        character_profile = await self._get_character_profile(character_name)
        
        prompt = f"""
Ты - {character_name}. 

ЛИЧНОСТЬ И ХАРАКТЕРИСТИКИ:
{character_profile}

РЕЛЕВАНТНЫЙ КОНТЕКСТ ИЗ ТВОИХ ПРЕДЫДУЩИХ СООБЩЕНИЙ:
{context}

ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
{user_query}

ИНСТРУКЦИЯ:
Ответь как {character_name}, используя свою личность и опираясь на контекст выше. 
Сохраняй характерный стиль речи и манеру поведения.
Если в контексте нет релевантной информации, отвечай исходя из своей личности.
"""
        
        return prompt.strip()

# Celery задачи для асинхронной обработки
@celery_app.task
def process_rag_task(character_name: str, user_query: str):
    """Асинхронная обработка RAG запроса"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    rag_manager = EnhancedRAGManager()
    result = loop.run_until_complete(
        rag_manager.process_character_request(character_name, user_query)
    )
    
    return result
