from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import topic_crud, message_crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# Добавляем фильтр nl2br для Jinja2
def nl2br(value):
    """Конвертирует переносы строк в HTML <br> теги"""
    return value.replace("\n", "<br>\n") if value else ""


templates.env.filters["nl2br"] = nl2br


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Главная страница со списком тем"""
    topics = await topic_crud.get_topics_list(db)

    # Добавляем количество сообщений для каждой темы
    for topic in topics:
        messages = await message_crud.get_topic_messages(db, topic.id)
        topic.message_count = len(messages)

    return templates.TemplateResponse("index.html", {"request": request, "topics": topics})


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
