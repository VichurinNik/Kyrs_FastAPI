from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings

# Импортируем модели для регистрации в Base.metadata
from models.base import Base
from models.product import Product  # noqa: F401

DATABASE_URL = settings.database_url

# Создание асинхронного движка базы данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def init_db():
    """
    Инициализация базы данных:
    - Удаляет все существующие таблицы (для чистоты эксперимента)
    - Создает таблицы заново на основе зарегистрированных моделей
    """
    async with engine.begin() as conn:
        # Для чистоты эксперимента будем удалять таблицы и пересоздавать их
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)