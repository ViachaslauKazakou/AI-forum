from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://username:password@localhost:5432/forum_db"
)

# Создаем асинхронный движок базы данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency для получения сессии базы данных
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
