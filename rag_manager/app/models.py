"""
Модели базы данных
"""
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base


class Embedding(Base):
    """Таблица эмбеддингов"""
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())


class MessageEmbedding(Base):
    """Таблица эмбеддингов сообщений форума"""
    __tablename__ = "message_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, nullable=False, index=True)
    topic_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())


class UserKnowledgeRecord(Base):
    """Таблица знаний пользователей"""
    __tablename__ = "user_knowledge"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    personality = Column(Text)
    background = Column(Text)
    expertise = Column(JSON)  # List[str]
    communication_style = Column(Text)
    preferences = Column(JSON)  # Dict
    file_path = Column(String(255))  # Путь к JSON файлу
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
