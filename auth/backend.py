# auth/backend.py
"""
Модуль для настройки механизма аутентификации через JWT токены.
"""
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

# Импортируем настройки проекта
from fastapi_shop.core.config import settings

# Транспорт для передачи токена в заголовке Authorization: Bearer <token>
bearer_transport = BearerTransport(tokenUrl="/auth/login")


# Функция для создания стратегии JWT
def get_jwt_strategy() -> JWTStrategy:
    """
    Создаёт стратегию JWT для аутентификации.

    Returns:
        JWTStrategy: Стратегия с указанным секретным ключом и временем жизни токена.
    """
    return JWTStrategy(
        secret=settings.SECRET_KEY,  # Секретный ключ из настроек
        lifetime_seconds=3600,  # Время жизни токена: 1 час (3600 секунд)
    )


# Backend аутентификации, объединяющий транспорт и стратегию
auth_backend = AuthenticationBackend(
    name="jwt",  # Имя backend'а
    transport=bearer_transport,  # Транспорт для передачи токена
    get_strategy=get_jwt_strategy,  # Функция для получения стратегии
)