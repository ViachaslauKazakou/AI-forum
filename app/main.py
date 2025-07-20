from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
from app.api import router as api_router
from app.web import router as web_router
from app.admin_api import router as admin_api_router
from app.admin_web import router as admin_web_router
from app.database import engine
from app.models.models import Base

# Создаем приложение FastAPI
app = FastAPI(title="Форум", description="Простой форум на FastAPI", version="1.0.0")

# Подключаем статические файлы (если нужны)
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем роуты
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(admin_api_router, prefix="/api", tags=["Admin API"])
app.include_router(web_router, tags=["Web"])
app.include_router(admin_web_router, tags=["Admin Web"])


@app.on_event("startup")
async def startup_event():
    """Создание таблиц при запуске приложения"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединений при завершении"""
    await engine.dispose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
