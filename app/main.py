import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
from app.urls.api_url import router as api_router
from app.urls.web_url import router as web_router
from app.urls.admin_url import router as admin_api_router
from app.urls.admin_web_url import router as admin_web_router

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# settings = get_settings
# Создаем приложение FastAPI
app = FastAPI(title="Форум", description="Простой форум на FastAPI", version="1.0.0")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # Запуск
    logger.info("Starting Forum service...")

    # try:
    #     # Инициализация БД (можно пропустить в dev режиме)
    #     if settings.skip_db_init:
    #         logger.info("Skipping database initialization (SKIP_DB_INIT=true)")
    #     else:
    #         logger.info("Initializing database...")
    #         await init_db()

    #     # Инициализация кэша знаний
    #     # logger.info("Initializing knowledge cache...")
    #     # knowledge_service = KnowledgeService()
    #     # await knowledge_service.warm_cache()

    #     logger.info("RAG Manager service started successfully")

    # except Exception as e:
    #     logger.error(f"Failed to start RAG Manager service: {e}")
    #     raise

    yield

    # Завершение
    logger.info("Shutting down RAG Manager service...")
# Подключаем статические файлы (если нужны)
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем роуты
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(admin_api_router, prefix="/api", tags=["Admin API"])
app.include_router(web_router, tags=["Web"])
app.include_router(admin_web_router, tags=["Admin Web"])


# @app.on_event("startup")
# async def startup_event():
#     """Создание таблиц при запуске приложения"""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# @app.on_event("shutdown")
# async def shutdown_event():
#     """Закрытие соединений при завершении"""
#     await engine.dispose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
