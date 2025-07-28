-- Инициализация базы данных с pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Создаем таблицу для хранения эмбеддингов
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 размерность
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаем индекс для быстрого поиска по векторам
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx 
ON embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Создаем таблицу для хранения эмбеддингов сообщений форума
CREATE TABLE IF NOT EXISTS message_embeddings (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для поиска по эмбеддингам сообщений
CREATE INDEX IF NOT EXISTS message_embeddings_embedding_idx 
ON message_embeddings USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Индекс для поиска по message_id
CREATE INDEX IF NOT EXISTS message_embeddings_message_id_idx 
ON message_embeddings (message_id);

-- Индекс для поиска по topic_id
CREATE INDEX IF NOT EXISTS message_embeddings_topic_id_idx 
ON message_embeddings (topic_id);
