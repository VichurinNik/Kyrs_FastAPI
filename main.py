from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.config import settings
from core.database import init_db
from routes import products
from utils.telegram import send_telegram_notification


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения
    """
    # Код, который выполняется при запуске приложения
    await init_db()
    print("База данных инициализирована")

    yield  # Здесь приложение работает

    # Код, который выполняется при остановке приложения
    print("Приложение остановлено")


app = FastAPI(
    title="FastAPI Shop",
    description="Магазин товаров из мультсериала Rick and Morty",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутер продуктов
app.include_router(products.router, prefix="/products", tags=["products"])


@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в FastAPI Shop!",
        "docs": "http://127.0.0.1:8000/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    try:
        await send_telegram_notification("🟢 Сервер запущен и работает")
        return {"status": "healthy", "message": "Сервер работает, уведомление отправлено"}
    except Exception as e:
        return {"status": "healthy", "message": f"Сервер работает, но уведомление не отправлено: {str(e)}"}