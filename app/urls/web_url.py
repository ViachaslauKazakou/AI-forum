from fastapi import APIRouter, Depends, HTTPException, Request
from app.templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.managers.db_manager import topic_crud, message_crud, category_crud, subcategory_crud

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Главная страница со списком тем, сгруппированных по категориям"""
    # Получаем категории с количеством топиков
    categories_with_topics = await category_crud.get_categories_with_topic_count(db)
    
    # Получаем все активные топики с предзагруженными связями
    all_topics = await topic_crud.get_topics_list(db, limit=1000)
    
    # Для каждой категории получаем топики
    categories_data = []
    for item in categories_with_topics:
        category = item["category"]
        
        # Фильтруем топики этой категории
        category_topics = [t for t in all_topics if t.category_id == category.id]
        
        # Добавляем количество сообщений для каждой темы
        topics_with_counts = []
        for topic in category_topics[:10]:  # Показываем максимум 10 топиков на категорию
            messages = await message_crud.get_topic_messages(db, topic.id)
            topic_data = {
                "topic": topic,
                "message_count": len(messages)
            }
            topics_with_counts.append(topic_data)
        
        if topics_with_counts:  # Показываем только категории с топиками
            categories_data.append({
                "category": category,
                "topics": topics_with_counts,
                "total_topics": len(category_topics)
            })
    
    # Добавляем топики без категории
    uncategorized_topics = [t for t in all_topics if not t.category_id]
    
    uncategorized_with_counts = []
    for topic in uncategorized_topics[:10]:  # Показываем максимум 10 топиков
        messages = await message_crud.get_topic_messages(db, topic.id)
        topic_data = {
            "topic": topic,
            "message_count": len(messages)
        }
        uncategorized_with_counts.append(topic_data)

    # Получаем 10 последних сообщений из всех топиков
    recent_messages = await message_crud.get_recent_messages_with_topics(db, limit=5)

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "categories_data": categories_data,
        "uncategorized_topics": uncategorized_with_counts,
        "total_uncategorized": len(uncategorized_topics),
        "recent_messages": recent_messages
    })


@router.get("/topics/{topic_id}", response_class=HTMLResponse)
async def topic_detail(request: Request, topic_id: int, db: AsyncSession = Depends(get_db)):
    """Страница темы с сообщениями"""
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    messages = await message_crud.get_topic_messages(db, topic_id, limit=20)

    return templates.TemplateResponse("topic.html", {"request": request, "topic": topic, "messages": messages})


@router.get("/create-topic", response_class=HTMLResponse)
async def create_topic_form(request: Request, db: AsyncSession = Depends(get_db)):
    """Форма создания новой темы"""
    categories = await category_crud.get_categories_list(db)
    subcategories = await subcategory_crud.get_subcategories_list(db)
    return templates.TemplateResponse("create_topic.html", {
        "request": request,
        "categories": categories,
        "subcategories": subcategories
    })
