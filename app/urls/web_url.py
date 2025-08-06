from fastapi import APIRouter, Depends, HTTPException, Request
from app.templates_config import templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.managers.db_manager import topic_crud, message_crud

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Главная страница со списком тем"""
    topics = await topic_crud.get_topics_list(db)

    # Добавляем количество сообщений для каждой темы
    topics_with_counts = []
    for topic in topics:
        messages = await message_crud.get_topic_messages(db, topic.id)
        topic_data = {
            "topic": topic,
            "message_count": len(messages)
        }
        topics_with_counts.append(topic_data)

    return templates.TemplateResponse("index.html", {"request": request, "topics": topics_with_counts})


@router.get("/topics/{topic_id}", response_class=HTMLResponse)
async def topic_detail(request: Request, topic_id: int, db: AsyncSession = Depends(get_db)):
    """Страница темы с сообщениями"""
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    messages = await message_crud.get_topic_messages(db, topic_id, limit=20)

    return templates.TemplateResponse("topic.html", {"request": request, "topic": topic, "messages": messages})


@router.get("/create-topic", response_class=HTMLResponse)
async def create_topic_form(request: Request):
    """Форма создания новой темы"""
    return templates.TemplateResponse("create_topic.html", {"request": request})
