# auth/database.py
"""
Модуль для работы с базой данных пользователей.
Предоставляет Dependency для доступа к таблице пользователей через SQLAlchemy.
"""
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем нашу функцию для получения сессии и модель пользователя
from fastapi_shop.auth.core.database import get_db_session
from fastapi_shop.models.user import User


async def get_user_db(
        session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, int], None]:
    """
    Dependency для получения доступа к таблице пользователей.

    Args:
        session: Сессия SQLAlchemy, полученная через Dependency.

    Yields:
        SQLAlchemyUserDatabase: Объект для работы с таблицей пользователей.
    """
    # Создаём и возвращаем объект для работы с пользователями
    yield SQLAlchemyUserDatabase(session, User)