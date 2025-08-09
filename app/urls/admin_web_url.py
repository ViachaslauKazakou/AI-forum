from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_config import templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.managers.db_manager import user_crud, topic_crud, message_crud
# from app.models.pydantic_models import UserRole, Status
from app.models.pydantic_models import UserBaseModel
from shared_models.schemas import UserRole, Status
from app.ai_manager.forum_manager import ForumManager
from shared_models.schemas import MessageCreate, TopicCreate, TopicUpdate, MessageUpdate
import json
from app.database import async_session_maker
import logging
from sqlalchemy import insert, select, func
from shared_models.models import Task  # используем модель из shared_models (таблица "tasks")
from app.celery_tasks import process_task
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin-web"])


# =============================================================================
# ADMIN DASHBOARD
# =============================================================================


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """Главная страница админ-панели"""
    # Получаем статистику
    users = await user_crud.get_users_list(db, limit=5)
    topics = await topic_crud.get_all_topics(db, limit=5)
    messages = await message_crud.get_all_messages(db, limit=5)

    # Подсчитываем общее количество
    all_users = await user_crud.get_users_list(db, limit=1000)
    all_topics = await topic_crud.get_all_topics(db, limit=1000)
    all_messages = await message_crud.get_all_messages(db, limit=1000)

    # Количество задач
    tasks_count = 0
    try:
        res = await db.execute(select(func.count()).select_from(Task))
        tasks_count = int(res.scalar() or 0)
    except Exception as e:
        logger.warning(f"Не удалось получить количество задач: {e}")

    stats = {
        "users_count": len(all_users),
        "topics_count": len(all_topics),
        "messages_count": len(all_messages),
        "tasks_count": tasks_count,
    }

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "stats": stats,
            "recent_users": users,
            "recent_topics": topics,
            "recent_messages": messages,
        },
    )


# =============================================================================
# USER MANAGEMENT
# =============================================================================


@router.get("/users", response_class=HTMLResponse)
async def admin_users_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Список пользователей"""
    users = await user_crud.get_users_list(db, limit=100)
    return templates.TemplateResponse("admin/users_list.html", {"request": request, "users": users})


@router.get("/users/create", response_class=HTMLResponse)
async def admin_users_create_form(request: Request):
    """Форма создания пользователя"""
    return templates.TemplateResponse(
        "admin/users_create.html",
        {
            "request": request,
            "user_roles": [role.value for role in UserRole],
            "user_statuses": [status.value for status in Status],
        },
    )


@router.post("/users/create")
async def admin_users_create(
    request: Request,
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    user_type: str = Form(...),
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Создание пользователя"""

    try:
        user_data = UserBaseModel(
            username=username,
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=password,
            user_type=UserRole(user_type),
            status=Status(status),
        )

        # Проверяем уникальность
        existing_user = await user_crud.get_user_by_username(db, username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

        existing_email = await user_crud.get_user_by_email(db, email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        await user_crud.create_user(db, user_data)
        return RedirectResponse(url="/admin/users", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "admin/users_create.html",
            {
                "request": request,
                "error": str(e),
                "user_roles": [role.value for role in UserRole],
                "user_statuses": [status.value for status in Status],
                "form_data": {
                    "username": username,
                    "firstname": firstname,
                    "lastname": lastname,
                    "email": email,
                    "user_type": user_type,
                    "status": status,
                },
            },
        )


@router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def admin_users_edit_form(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    """Форма редактирования пользователя"""
    user = await user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return templates.TemplateResponse(
        "admin/users_edit.html",
        {
            "request": request,
            "user": user,
            "user_roles": [role.value for role in UserRole],
            "user_statuses": [status.value for status in Status],
        },
    )


@router.post("/users/{user_id}/edit")
async def admin_users_edit(
    request: Request,
    user_id: int,
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    user_type: str = Form(...),
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Редактирование пользователя"""
    from app.models.pydantic_models import UserBaseModel

    try:
        user_data = UserBaseModel(
            username=username,
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=password,
            user_type=UserRole(user_type),
            status=Status(status),
        )

        await user_crud.update_user(db, user_id, user_data)
        return RedirectResponse(url="/admin/users", status_code=303)

    except Exception as e:
        user = await user_crud.get_user_by_id(db, user_id)
        return templates.TemplateResponse(
            "admin/users_edit.html",
            {
                "request": request,
                "user": user,
                "error": str(e),
                "user_roles": [role.value for role in UserRole],
                "user_statuses": [status.value for status in Status],
            },
        )


@router.post("/users/{user_id}/delete")
async def admin_users_delete(user_id: int, db: AsyncSession = Depends(get_db)):
    """Удаление пользователя"""
    await user_crud.delete_user(db, user_id)
    return RedirectResponse(url="/admin/users", status_code=303)


# =============================================================================
# TOPIC MANAGEMENT
# =============================================================================


@router.get("/topics", response_class=HTMLResponse)
async def admin_topics_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Список тем"""
    topics = await topic_crud.get_all_topics(db, limit=100)
    return templates.TemplateResponse("admin/topics_list.html", {"request": request, "topics": topics})


@router.get("/topics/create", response_class=HTMLResponse)
async def admin_topics_create_form(request: Request, db: AsyncSession = Depends(get_db)):
    """Форма создания темы"""
    users = await user_crud.get_users_list(db, limit=100)
    return templates.TemplateResponse("admin/topics_create.html", {"request": request, "users": users})


@router.post("/topics/create")
async def admin_topics_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    user_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Создание темы"""

    try:
        topic_data = TopicCreate(title=title, description=description, user_id=user_id if user_id else None)

        await topic_crud.create_topic(db, topic_data)
        return RedirectResponse(url="/admin/topics", status_code=303)

    except Exception as e:
        users = await user_crud.get_users_list(db, limit=100)
        return templates.TemplateResponse(
            "admin/topics_create.html",
            {
                "request": request,
                "error": str(e),
                "users": users,
                "form_data": {
                    "title": title,
                    "description": description,
                    "user_id": user_id,
                },
            },
        )


@router.get("/topics/{topic_id}/edit", response_class=HTMLResponse)
async def admin_topics_edit_form(request: Request, topic_id: int, db: AsyncSession = Depends(get_db)):
    """Форма редактирования темы"""
    topic = await topic_crud.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    users = await user_crud.get_users_list(db, limit=100)
    return templates.TemplateResponse("admin/topics_edit.html", {"request": request, "topic": topic, "users": users})


@router.post("/topics/{topic_id}/edit")
async def admin_topics_edit(
    request: Request,
    topic_id: int,
    title: str = Form(...),
    description: str = Form(""),
    is_active: bool = Form(True),
    db: AsyncSession = Depends(get_db),
):
    """Редактирование темы"""

    try:
        topic_data = TopicUpdate(title=title, description=description, is_active=is_active)

        await topic_crud.update_topic(db, topic_id, topic_data)
        return RedirectResponse(url="/admin/topics", status_code=303)

    except Exception as e:
        topic = await topic_crud.get_topic_by_id(db, topic_id)
        users = await user_crud.get_users_list(db, limit=100)
        return templates.TemplateResponse(
            "admin/topics_edit.html",
            {
                "request": request,
                "topic": topic,
                "users": users,
                "error": str(e),
            },
        )


@router.post("/topics/{topic_id}/delete")
async def admin_topics_delete(topic_id: int, db: AsyncSession = Depends(get_db)):
    """Удаление темы"""
    await topic_crud.delete_topic(db, topic_id)
    return RedirectResponse(url="/admin/topics", status_code=303)


# =============================================================================
# MESSAGE MANAGEMENT
# =============================================================================


@router.get("/messages", response_class=HTMLResponse)
async def admin_messages_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Список сообщений"""
    messages = await message_crud.get_all_messages(db, limit=100)
    return templates.TemplateResponse("admin/messages_list.html", {"request": request, "messages": messages})


@router.get("/messages/{message_id}/edit", response_class=HTMLResponse)
async def admin_messages_edit_form(request: Request, message_id: int, db: AsyncSession = Depends(get_db)):
    """Форма редактирования сообщения"""
    message = await message_crud.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    return templates.TemplateResponse("admin/messages_edit.html", {"request": request, "message": message})


@router.post("/messages/{message_id}/edit")
async def admin_messages_edit(
    request: Request,
    message_id: int,
    content: str = Form(...),
    author_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Редактирование сообщения"""

    try:
        message_data = MessageUpdate(content=content, author_name=author_name)

        await message_crud.update_message(db, message_id, message_data)
        return RedirectResponse(url="/admin/messages", status_code=303)

    except Exception as e:
        message = await message_crud.get_message_by_id(db, message_id)
        return templates.TemplateResponse(
            "admin/messages_edit.html",
            {
                "request": request,
                "message": message,
                "error": str(e),
            },
        )


@router.post("/messages/{message_id}/delete")
async def admin_messages_delete(message_id: int, db: AsyncSession = Depends(get_db)):
    """Удаление сообщения"""
    await message_crud.delete_message_by_id(db, message_id)
    return RedirectResponse(url="/admin/messages", status_code=303)


# =============================================================================
# AI MESSAGE MANAGEMENT
# =============================================================================

@router.get("/users/{user_id}/ai-messages/create", response_class=HTMLResponse)
async def admin_ai_messages_create_form(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    """Форма создания AI сообщения"""
    topics = await topic_crud.get_all_topics(db, limit=100)
    return templates.TemplateResponse("admin/ai_messages.html", {"request": request, "topics": topics, "user_id": user_id})


async def generate_and_save_ai_message(topic_id: str, user_id: str):
    """Создание AI задачи: запись в таблицу tasks и постановка в очередь Celery"""

    try:
        topic_id_int = int(topic_id)
        user_id_int = int(user_id)

        payload = {
            "topic_id": topic_id_int,
            "user_id": user_id_int,
        }

        task_uuid = str(uuid.uuid4())
        question_text = f"Generate AI message for topic {topic_id_int} and user {user_id_int}"
        context_text = json.dumps(payload)

        async with async_session_maker() as db:
            # Вставляем запись задачи и получаем её id (таблица "tasks")
            stmt = (
                insert(Task)
                .values(
                    task_id=task_uuid,
                    user_id=user_id_int,
                    topic_id=topic_id_int,
                    question=question_text,
                    context=context_text,
                    status="pending",
                )
                .returning(Task.id)
            )
            result = await db.execute(stmt)
            task_id_db = result.scalar_one()
            await db.commit()

        # Отправляем задачу воркеру Celery по id записи
        process_task.delay(task_id_db)

        logger.info(
            f"🚀 Задача поставлена в очередь: task_id={task_id_db}, topic_id={topic_id_int}, user_id={user_id_int}"
        )

    except ValueError as ve:
        logger.error(f"❌ Ошибка валидации параметров: {ve}")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка постановки задачи: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


@router.post("/messages/ai/create")
async def admin_ai_messages_create(
    topic_id: str = Form(...),
    user_id: str = Form(...)
):
    """Создание ИИ сообщения через таблицу tasks и Celery"""
    try:
        # Валидация входных данных
        int(topic_id)
        int(user_id)

        # Создаём запись в tasks и отправляем в Celery
        await generate_and_save_ai_message(topic_id, user_id)

        logger.info(f"🚀 Задача добавлена в очередь для topic_id={topic_id}, user_id={user_id}")
        return RedirectResponse(
            url=f"/topics/{topic_id}?generating=true&ai_user={user_id}",
            status_code=303
        )

    except ValueError:
        logger.error(f"❌ Неверные параметры: topic_id={topic_id}, user_id={user_id}")
        raise HTTPException(status_code=400, detail="Неверные параметры запроса")
    except Exception as e:
        logger.error(f"❌ Ошибка обработки запроса: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# =============================================================================
# TASK MANAGEMENT
# =============================================================================


@router.get("/tasks", response_class=HTMLResponse)
async def admin_tasks_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Список задач (tasks)"""
    try:
        res = await db.execute(
            select(Task).order_by(Task.id.desc()).limit(50)
        )
        tasks = res.scalars().all()
    except Exception as e:
        logger.error(f"Ошибка получения списка задач: {e}")
        tasks = []
    return templates.TemplateResponse("admin/tasks_list.html", {"request": request, "tasks": tasks})


@router.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def admin_tasks_edit_form(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    """Форма редактирования задачи"""
    res = await db.execute(select(Task).where(Task.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return templates.TemplateResponse("admin/tasks_edit.html", {"request": request, "task": task})


@router.post("/tasks/{task_id}/edit")
async def admin_tasks_edit(
    request: Request,
    task_id: int,
    status: str = Form(...),
    result: str = Form("") ,
    error_message: str = Form("") ,
    db: AsyncSession = Depends(get_db),
):
    """Обновление полей задачи"""
    res = await db.execute(select(Task).where(Task.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task.status = status
    if hasattr(task, "result"):
        task.result = result or None
    if hasattr(task, "error_message"):
        task.error_message = error_message or None
    await db.commit()
    return RedirectResponse(url="/admin/tasks", status_code=303)


@router.post("/tasks/{task_id}/retry")
async def admin_tasks_retry(task_id: int, db: AsyncSession = Depends(get_db)):
    """Переотправить задачу в Celery по ID записи"""
    # убедимся, что задача существует
    res = await db.execute(select(Task).where(Task.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    # ставим статус pending и отправляем
    task.status = "pending"
    await db.commit()
    process_task.delay(task_id)
    return RedirectResponse(url="/admin/tasks", status_code=303)


