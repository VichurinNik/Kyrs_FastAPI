# auth/manager.py
"""
Модуль с бизнес-логикой управления пользователями.
Содержит UserManager с методами регистрации, верификации, сброса пароля и т.д.
"""
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin

# Импортируем наши настройки и модель
from fastapi_shop.core import settings
from models.user import User
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

# Импортируем нашу функцию для получения сессии и модель пользователя
from fastapi_shop.core.database import get_db_session
from models.user import User
# Импортируем Dependency для доступа к БД пользователей
from database import get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Менеджер пользователей с поддержкой целочисленных ID.
    """
    # Секретные ключи для токенов сброса пароля и верификации
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(
            self, user: User, request: Optional[Request] = None
    ):
        """
        Callback, вызываемый после успешной регистрации пользователя.

        Args:
            user: Зарегистрированный пользователь.
            request: Объект запроса (опционально).
        """
        # Здесь можно добавить логику отправки приветственного письма,
        # уведомления в Telegram и т.д.
        print(f"Пользователь {user.id} зарегистрирован.")
        print(f"Email: {user.email}")


async def get_user_manager(
        user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """
    Dependency для получения менеджера пользователей.

    Args:
        user_db: Объект для работы с БД пользователей, полученный через Dependency.

    Yields:
        UserManager: Менеджер пользователей.
    """
    # Создаём и возвращаем менеджер пользователей
    yield UserManager(user_db)