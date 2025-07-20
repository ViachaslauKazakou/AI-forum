from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.crud import user_crud, topic_crud, message_crud
from app.models.pydantic_models import UserRole, Status
from app.ai_manager.forum_manager import ForumManager
from app.schemas import MessageCreate

router = APIRouter(prefix="/admin", tags=["admin-web"])
templates = Jinja2Templates(directory="app/templates")


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

    stats = {
        "users_count": len(all_users),
        "topics_count": len(all_topics),
        "messages_count": len(all_messages),
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
    from app.schemas import TopicCreate

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
    from app.schemas import TopicUpdate

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
    from app.schemas import MessageUpdate

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


@router.get("/messages/ai/create", response_class=HTMLResponse)
async def admin_ai_messages_create(request: Request, topic_id: str, user_id: str, db: AsyncSession = Depends(get_db)):
    """Создание AI сообщения"""
    ai_manager = ForumManager()
    # Получаем последнее сообщение из темы
    last_message = await message_crud.get_topic_messages(db, int(topic_id), limit=1)
    if not last_message:
        raise HTTPException(status_code=404, detail="Нет сообщений в теме")
    # Получаем юзернэйм по user_id
    user = await user_crud.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Пример 1: Ответ от конкретного персонажа
    print(f"🎭 Ответ от {user.username}:")
    response = ai_manager.ask_as_character(
        last_message[0].content, 
        user.username, 
        mood="sarcastic"
    )
    print(f"{user.username}: {response['result']}")
    # Сохраняем AI сообщение
    message = MessageCreate(
        content=response['result'],
        author_name=user.username,
        topic_id=int(topic_id),
        user_id=int(user_id),
        parent_id=int(last_message[0].id) if last_message else None
    )
    await message_crud.create_message(db, message)
    return RedirectResponse(url="/admin/messages", status_code=200)

