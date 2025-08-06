from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.managers.db_manager import topic_crud, message_crud

router = APIRouter(prefix="/api/ai", tags=["Ai-posting"])
templates = Jinja2Templates(directory="app/templates")


# Добавляем фильтр nl2br для Jinja2
def nl2br(value):
    """Конвертирует переносы строк в HTML <br> теги"""
    return value.replace("\n", "<br>\n") if value else ""


templates.env.filters["nl2br"] = nl2br


@router.post("/add", response_class=HTMLResponse)
async def add_ai_post(request: Request):
    """Форма добавления AI поста"""
    return templates.TemplateResponse("add_ai_post.html", {"request": request})


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