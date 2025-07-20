from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.crud import topic_crud, message_crud
from app.schemas import (
    TopicCreate,
    TopicResponse,
    TopicWithMessages,
    MessageCreate,
    MessageResponse,
    TopicList,
)

router = APIRouter()


@router.get("/topics", response_model=List[TopicList])
async def get_topics(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получить список тем"""
    topics = await topic_crud.get_topics_list(db, skip=skip, limit=limit)
    return topics


@router.post("/topics", response_model=TopicResponse)
async def create_topic(topic: TopicCreate, db: AsyncSession = Depends(get_db)):
    """Создать новую тему"""
    return await topic_crud.create_topic(db, topic)


@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: int, db: AsyncSession = Depends(get_db)):
    """Получить тему по ID"""
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    return topic


@router.get("/topics/{topic_id}/full", response_model=TopicWithMessages)
async def get_topic_with_messages(topic_id: int, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Получить тему со всеми сообщениями"""
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    messages = await message_crud.get_topic_messages(db, topic_id, limit)

    # Создаем объект с сообщениями
    return TopicWithMessages(
        id=topic.id,
        title=topic.title,
        description=topic.description,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        is_active=topic.is_active,
        messages=messages,
    )


@router.get("/topics/{topic_id}/messages", response_model=List[MessageResponse])
async def get_topic_messages(topic_id: int, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Получить сообщения темы"""
    # Проверяем существование темы
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    messages = await message_crud.get_topic_messages(db, topic_id, limit)
    return messages


@router.post("/messages", response_model=MessageResponse)
async def create_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    """Создать новое сообщение"""
    # Проверяем существование темы
    topic = await topic_crud.get_topic_by_id(db, message.topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    # Если указан parent_id, проверяем существование родительского сообщения
    if message.parent_id:
        parent_message = await message_crud.get_message_by_id(db, message.parent_id)
        if not parent_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительское сообщение не найдено",
            )
        if parent_message.topic_id != message.topic_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Родительское сообщение должно быть из той же темы",
            )

    return await message_crud.create_message(db, message)
