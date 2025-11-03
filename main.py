from fastapi import FastAPI
from config import settings

# Импортируем роутеры
from routes.products import router as products_router

app = FastAPI(
    title="Ваше ФИО — Домашнее задание №33",
    description="Рефакторинг FastAPI проекта: модульная структура с APIRouter и конфигурацией",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(products_router)


@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о приложении"""
    # Маскируем ключ для безопасности
    masked_key = settings.tg_bot_key[:10] + "..." if settings.tg_bot_key else "не установлен"

    return {
        "message": "Добро пожаловать в API магазина Рика и Морти!",
        "version": "1.0.0",
        "features": [
            "Полный CRUD для продуктов",
            "Поиск и фильтрация",
            "Модульная архитектура с APIRouter"
        ],
        "telegram_bot_key": masked_key,
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки здоровья приложения"""
    return {"status": "healthy", "message": "API работает корректно"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)