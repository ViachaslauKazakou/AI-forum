"""
Модуль для работы с pgvector и эмбеддингами в PostgreSQL
"""
import asyncio
import json
from typing import List, Optional, Tuple

import asyncpg
from pgvector.asyncpg import register_vector


class EmbeddingManager:
    """Менеджер для работы с эмбеддингами в PostgreSQL с pgvector"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def initialize(self):
        """Инициализация пула соединений"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            init=self._init_connection
        )
    
    async def _init_connection(self, connection):
        """Инициализация каждого соединения для работы с pgvector"""
        await register_vector(connection)
    
    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
    
    async def insert_embedding(
        self, 
        content: str, 
        embedding: List[float], 
        metadata: Optional[dict] = None
    ) -> int:
        """
        Вставка эмбеддинга в базу данных
        
        Args:
            content: Текстовый контент
            embedding: Вектор эмбеддинга (список чисел)
            metadata: Дополнительные метаданные
            
        Returns:
            ID вставленной записи
        """
        async with self.pool.acquire() as connection:
            result = await connection.fetchval(
                """
                INSERT INTO embeddings (content, embedding, metadata)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                content,
                embedding,
                json.dumps(metadata) if metadata else None
            )
            return result
    
    async def search_similar(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        similarity_threshold: float = 0.8
    ) -> List[Tuple[int, str, float, dict]]:
        """
        Поиск похожих эмбеддингов
        
        Args:
            query_embedding: Вектор запроса
            limit: Максимальное количество результатов
            similarity_threshold: Порог схожести (cosine similarity)
            
        Returns:
            Список кортежей (id, content, similarity, metadata)
        """
        async with self.pool.acquire() as connection:
            results = await connection.fetch(
                """
                SELECT 
                    id, 
                    content, 
                    1 - (embedding <=> $1) as similarity,
                    metadata
                FROM embeddings
                WHERE 1 - (embedding <=> $1) > $2
                ORDER BY embedding <=> $1
                LIMIT $3
                """,
                query_embedding,
                similarity_threshold,
                limit
            )
            
            return [
                (
                    row['id'], 
                    row['content'], 
                    float(row['similarity']),
                    json.loads(row['metadata']) if row['metadata'] else {}
                )
                for row in results
            ]
    
    async def insert_message_embedding(
        self,
        message_id: int,
        topic_id: int,
        content: str,
        embedding: List[float],
        metadata: Optional[dict] = None
    ) -> int:
        """
        Вставка эмбеддинга сообщения форума
        
        Args:
            message_id: ID сообщения
            topic_id: ID топика
            content: Содержимое сообщения
            embedding: Вектор эмбеддинга
            metadata: Дополнительные метаданные
            
        Returns:
            ID вставленной записи
        """
        async with self.pool.acquire() as connection:
            result = await connection.fetchval(
                """
                INSERT INTO message_embeddings (message_id, topic_id, content, embedding, metadata)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                message_id,
                topic_id,
                content,
                embedding,
                json.dumps(metadata) if metadata else None
            )
            return result
    
    async def search_similar_messages(
        self,
        query_embedding: List[float],
        topic_id: Optional[int] = None,
        limit: int = 10,
        similarity_threshold: float = 0.8
    ) -> List[Tuple[int, int, int, str, float, dict]]:
        """
        Поиск похожих сообщений форума
        
        Args:
            query_embedding: Вектор запроса
            topic_id: ID топика для фильтрации (опционально)
            limit: Максимальное количество результатов
            similarity_threshold: Порог схожести
            
        Returns:
            Список кортежей (id, message_id, topic_id, content, similarity, metadata)
        """
        if topic_id:
            query = """
                SELECT 
                    id, message_id, topic_id, content,
                    1 - (embedding <=> $1) as similarity,
                    metadata
                FROM message_embeddings
                WHERE topic_id = $2 AND 1 - (embedding <=> $1) > $3
                ORDER BY embedding <=> $1
                LIMIT $4
            """
            params = [query_embedding, topic_id, similarity_threshold, limit]
        else:
            query = """
                SELECT 
                    id, message_id, topic_id, content,
                    1 - (embedding <=> $1) as similarity,
                    metadata
                FROM message_embeddings
                WHERE 1 - (embedding <=> $1) > $2
                ORDER BY embedding <=> $1
                LIMIT $3
            """
            params = [query_embedding, similarity_threshold, limit]
        
        async with self.pool.acquire() as connection:
            results = await connection.fetch(query, *params)
            
            return [
                (
                    row['id'],
                    row['message_id'], 
                    row['topic_id'],
                    row['content'], 
                    float(row['similarity']),
                    json.loads(row['metadata']) if row['metadata'] else {}
                )
                for row in results
            ]


# Пример использования
async def example_usage():
    """Пример использования EmbeddingManager"""
    
    # Подключение к базе данных
    DATABASE_URL = "postgresql://docker:docker@localhost:5433/postgres"
    manager = EmbeddingManager(DATABASE_URL)
    
    try:
        await manager.initialize()
        
        # Пример вставки эмбеддинга (создаем фиктивный вектор)
        dummy_embedding = [0.1] * 1536  # OpenAI ada-002 размерность
        
        embedding_id = await manager.insert_embedding(
            content="Пример текста для поиска",
            embedding=dummy_embedding,
            metadata={"source": "test", "author": "system"}
        )
        
        print(f"Вставлен эмбеддинг с ID: {embedding_id}")
        
        # Пример поиска
        results = await manager.search_similar(
            query_embedding=dummy_embedding,
            limit=5,
            similarity_threshold=0.9
        )
        
        print(f"Найдено {len(results)} похожих записей")
        for result in results:
            print(f"ID: {result[0]}, Similarity: {result[2]:.3f}")
            
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
    asyncio.run(example_usage())
