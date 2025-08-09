from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.managers.db_manager import topic_crud, message_crud, category_crud, subcategory_crud
from shared_models.schemas import (
    TopicResponse,
    TopicWithMessages,
    MessageCreate,
    MessageResponse,
    TopicList,
)
from app.schemas.categories import TopicCreateWithCategories, CategoryResponse, SubcategoryResponse

router = APIRouter()


@router.get("/topics", response_model=List[TopicList])
async def get_topics(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получить список тем"""
    topics = await topic_crud.get_topics_list(db, skip=skip, limit=limit)
    return topics


@router.post("/topics", response_model=TopicResponse)
async def create_topic(topic: TopicCreateWithCategories, db: AsyncSession = Depends(get_db)):
    """Создать новую тему"""
    # Преобразуем в формат, который понимает CRUD
    from shared_models.schemas import TopicCreate
    topic_data = TopicCreate(
        title=topic.title,
        description=topic.description,
        user_id=topic.user_id
    )
    
    # Добавляем категории через атрибуты
    if topic.category_id:
        topic_data.category_id = topic.category_id
    if topic.subcategory_id:
        topic_data.subcategory_id = topic.subcategory_id
    
    return await topic_crud.create_topic(db, topic_data)


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
    from shared_models.schemas import MessageResponse
    message_responses = [
        MessageResponse(
            id=msg.id,
            content=msg.content,
            author_name=msg.author_name,
            topic_id=msg.topic_id,
            parent_id=msg.parent_id,
            user_id=getattr(msg, 'user_id', None),
            created_at=msg.created_at,
            updated_at=msg.updated_at
        ) for msg in messages
    ]
    
    return TopicWithMessages(
        id=topic.id,
        title=topic.title,
        description=topic.description,
        created_at=topic.created_at,
        updated_at=topic.updated_at,
        is_active=topic.is_active,
        user_id=getattr(topic, 'user_id', None),
        category_id=getattr(topic, 'category_id', None),
        subcategory_id=getattr(topic, 'subcategory_id', None),
        messages=message_responses,
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


# =============================================================================
# CATEGORY API
# =============================================================================

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получить список категорий"""
    categories = await category_crud.get_categories_list(db, skip=skip, limit=limit)
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Получить категорию по ID"""
    category = await category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
    return category


# =============================================================================
# SUBCATEGORY API
# =============================================================================

@router.get("/subcategories", response_model=List[SubcategoryResponse])
async def get_subcategories(category_id: Optional[int] = None, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Получить список подкатегорий"""
    subcategories = await subcategory_crud.get_subcategories_list(db, category_id=category_id, skip=skip, limit=limit)
    return subcategories


@router.get("/subcategories/{subcategory_id}", response_model=SubcategoryResponse)
async def get_subcategory(subcategory_id: int, db: AsyncSession = Depends(get_db)):
    """Получить подкатегорию по ID"""
    subcategory = await subcategory_crud.get_subcategory_by_id(db, subcategory_id)
    if not subcategory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Подкатегория не найдена")
    return subcategory
