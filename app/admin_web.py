from fastapi import APIRouter, Request, Depends, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.crud import user_crud, topic_crud, message_crud
from app.models.pydantic_models import UserRole, Status
from app.ai_manager.forum_manager import ForumManager
from app.models.schemas import MessageCreate
import json

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
    from app.models.schemas import TopicCreate

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
    from app.models.schemas import TopicUpdate

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
    from app.models.schemas import MessageUpdate

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
    """Создание AI сообщения в фоновом режиме"""
    from app.database import async_session_maker
    import logging
    import asyncio
    
    logger = logging.getLogger(__name__)
    
    try:
        # Преобразуем строки в числа с валидацией
        topic_id_int = int(topic_id)
        user_id_int = int(user_id)
        
        logger.info(f"🚀 Начало генерации ИИ сообщения: topic_id={topic_id_int}, user_id={user_id_int}")
        
        # Создаем новую сессию БД для фоновой задачи
        async with async_session_maker() as db:
            try:
                # Проверяем существование темы
                topic = await topic_crud.get_topic_by_id(db, topic_id_int)
                if not topic:
                    logger.error(f"❌ Тема {topic_id_int} не найдена")
                    return
                
                # Получаем последние сообщения из темы (больше контекста)
                recent_messages = await message_crud.get_topic_messages(db, topic_id_int, limit=5)
                if not recent_messages:
                    logger.error(f"❌ Нет сообщений в теме {topic_id_int}")
                    return
                
                # Получаем пользователя по user_id
                user = await user_crud.get_user_by_id(db, user_id_int)
                if not user:
                    logger.error(f"❌ Пользователь {user_id_int} не найден")
                    return
                
                logger.info(f"🎭 Генерация ответа от {user.username} для темы '{topic.title}'")
                
                # Создаем контекст из последних сообщений
                context = "\n".join([f"{msg.author_name}: {msg.content}" for msg in reversed(recent_messages[-3:])])
                last_message_content = recent_messages[0].content
                
                # Инициализируем ИИ менеджер
                ai_manager = ForumManager()
                
                # Создаем расширенный запрос с контекстом
                enhanced_query = f"Контекст последних сообщений:\n{context}\n\nОтветь на: {last_message_content}"
                
                # Генерируем ответ от ИИ персонажа асинхронно
                logger.info(f"🤖 Запуск генерации ответа для персонажа {user.username}")
                
                # Добавляем таймаут для генерации (максимум 60 секунд)
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        ai_manager.ask_as_character,
                        enhanced_query,  # Используем расширенный запрос с контекстом
                        user.username,
                        mood="sarcastic"
                    ),
                    timeout=60.0
                )
                
                logger.info(f"📝 Получен ответ от ИИ: {str(response)[:100]}...")
                
                # Обрабатываем ответ
                answer = None
                if isinstance(response, dict):
                    if 'result' in response:
                        try:
                            # Пытаемся парсить как JSON
                            if isinstance(response['result'], str):
                                result = json.loads(response['result'])
                                answer = result.get('content', response['result'])
                            else:
                                answer = response['result']
                        except json.JSONDecodeError:
                            # Если не JSON, используем как есть
                            answer = response['result']
                    else:
                        answer = str(response)
                elif isinstance(response, str):
                    try:
                        result = json.loads(response)
                        answer = result.get('content', response)
                    except json.JSONDecodeError:
                        answer = response
                else:
                    answer = str(response)
                
                if not answer or answer.strip() == "":
                    logger.error("❌ ИИ вернул пустой ответ")
                    return
                
                logger.info(f"✅ Обработанный ответ: {answer[:100]}...")
                
                # Создаем сообщение
                message_data = MessageCreate(
                    content=answer,
                    author_name=user.username,
                    topic_id=topic_id_int,
                    user_id=user_id_int,
                    parent_id=recent_messages[0].id if recent_messages else None
                )
                
                # Сохраняем в БД
                created_message = await message_crud.create_message(db, message_data)
                
                logger.info(f"✅ ИИ сообщение создано: ID={created_message.id}, тема={topic.title}")
                
                # Фиксируем изменения в БД
                await db.commit()
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Таймаут генерации ИИ сообщения для темы {topic_id_int}")
                await db.rollback()
            except Exception as db_error:
                logger.error(f"❌ Ошибка работы с БД: {db_error}")
                await db.rollback()
                raise
                
    except ValueError as ve:
        logger.error(f"❌ Ошибка валидации параметров: {ve}")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка создания ИИ сообщения: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


@router.post("/messages/ai/create")
async def admin_ai_messages_create(
    background_tasks: BackgroundTasks,
    topic_id: str = Form(...),
    user_id: str = Form(...)
):
    """Создание ИИ сообщения с асинхронной обработкой"""
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Валидация входных данных
        topic_id_int = int(topic_id)
        user_id_int = int(user_id)
        
        logger.info(f"📨 Получен запрос на создание ИИ сообщения: topic_id={topic_id_int}, user_id={user_id_int}")
        
        # Запуск в фоне с улучшенной обработкой
        background_tasks.add_task(
            generate_and_save_ai_message,
            topic_id,
            user_id
        )
        
        logger.info(f"🚀 Задача добавлена в очередь для topic_id={topic_id_int}")
        
        # Немедленный редирект с индикатором
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


