# models/user.py
"""
Модель пользователя для SQLAlchemy.
"""
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# Импортируем базовый класс моделей


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    Модель пользователя.

    Наследует:
    - SQLAlchemyBaseUserTable[int]: базовый класс FastAPI Users для таблицы пользователей
    - Base: базовый класс SQLAlchemy из нашего проекта

    Attributes:
        __tablename__: Имя таблицы в БД
        id: Первичный ключ пользователя
    """
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,  # Поле является первичным ключом
        index=True  # Создать индекс для ускорения поиска
    )

    # Остальные поля (email, hashed_password, is_active, is_superuser, is_verified)
    # автоматически наследуются от SQLAlchemyBaseUserTable