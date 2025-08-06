from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import get_settings

# Получаем настройки
settings = get_settings

print(f"🔗 Подключение к базе данных: {settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://').split('@')[0]}@***")

# Создаем асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Установите True для отладки SQL запросов
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Пересоздание соединений каждый час
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency для получения сессии базы данных
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
