from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.managers.db_manager import user_crud, topic_crud, message_crud
from shared_models.schemas import (
    TopicCreate,
    TopicResponse,
    TopicUpdate,
    MessageCreate,
    MessageResponse,
    MessageUpdate,
)
from app.models.pydantic_models import UserBaseModel, GetUserModel

router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# USER MANAGEMENT
# =============================================================================


@router.get("/users", response_model=List[GetUserModel])
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получить список всех пользователей"""
    users = await user_crud.get_users_list(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=GetUserModel)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получить пользователя по ID"""
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return user


@router.post("/users", response_model=GetUserModel)
async def create_user(user: UserBaseModel, db: AsyncSession = Depends(get_db)):
    """Создать нового пользователя"""
    # Проверяем уникальность username
    existing_user = await user_crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким именем уже существует"
        )

    # Проверяем уникальность email
    existing_email = await user_crud.get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")

    return await user_crud.create_user(db, user)


@router.put("/users/{user_id}", response_model=GetUserModel)
async def update_user(user_id: int, user_data: UserBaseModel, db: AsyncSession = Depends(get_db)):
    """Обновить пользователя"""
    # Проверяем существование пользователя
    existing_user = await user_crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # Проверяем уникальность username (если изменился)
    if existing_user.username != user_data.username:
        username_exists = await user_crud.get_user_by_username(db, user_data.username)
        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким именем уже существует"
            )

    # Проверяем уникальность email (если изменился)
    if existing_user.email != user_data.email:
        email_exists = await user_crud.get_user_by_email(db, user_data.email)
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует"
            )

    updated_user = await user_crud.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return updated_user


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить пользователя"""
    success = await user_crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return {"message": "Пользователь успешно удален"}


# =============================================================================
# TOPIC MANAGEMENT
# =============================================================================


@router.get("/topics", response_model=List[TopicResponse])
async def get_all_topics(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получить все темы (включая неактивные)"""
    topics = await topic_crud.get_all_topics(db, skip=skip, limit=limit)
    return topics


@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: int, db: AsyncSession = Depends(get_db)):
    """Получить тему по ID"""
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    return topic


@router.post("/topics", response_model=TopicResponse)
async def create_topic(topic: TopicCreate, db: AsyncSession = Depends(get_db)):
    """Создать новую тему"""
    # Если указан user_id, проверяем существование пользователя
    if topic.user_id:
        user = await user_crud.get_user_by_id(db, topic.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return await topic_crud.create_topic(db, topic)


@router.put("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(topic_id: int, topic_data: TopicUpdate, db: AsyncSession = Depends(get_db)):
    """Обновить тему"""
    updated_topic = await topic_crud.update_topic(db, topic_id, topic_data)
    if not updated_topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    return updated_topic


@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить тему"""
    success = await topic_crud.delete_topic(db, topic_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    return {"message": "Тема успешно удалена"}


# =============================================================================
# MESSAGE MANAGEMENT
# =============================================================================


@router.get("/messages", response_model=List[MessageResponse])
async def get_all_messages(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получить все сообщения"""
    messages = await message_crud.get_all_messages(db, skip=skip, limit=limit)
    return messages


@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    """Получить сообщение по ID"""
    message = await message_crud.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сообщение не найдено")
    return message


@router.post("/messages", response_model=MessageResponse)
async def create_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    """Создать новое сообщение"""
    # Проверяем существование темы
    topic = await topic_crud.get_topic_by_id(db, message.topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    # Если указан user_id, проверяем существование пользователя
    if message.user_id:
        user = await user_crud.get_user_by_id(db, message.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

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


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(message_id: int, message_data: MessageUpdate, db: AsyncSession = Depends(get_db)):
    """Обновить сообщение"""
    updated_message = await message_crud.update_message(db, message_id, message_data)
    if not updated_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сообщение не найдено")

    return updated_message


@router.delete("/messages/{message_id}")
async def delete_message(message_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить сообщение"""
    success = await message_crud.delete_message_by_id(db, message_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Сообщение не найдено")

    return {"message": "Сообщение успешно удалено"}


# =============================================================================
# AI MESSAGE MANAGEMENT
# =============================================================================


@router.get("/messages/ai/create", response_model=MessageResponse)
async def create_ai_message(topic_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """Создать AI сообщение"""
    # Проверяем существование темы
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    # Проверяем существование пользователя
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # Создаём AI сообщение
    message = await message_crud.create_ai_message(db, {"topic_id": topic_id, "user_id": user_id})

    return message
