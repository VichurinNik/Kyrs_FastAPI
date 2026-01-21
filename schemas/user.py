# schemas/user.py
"""
Pydantic-схемы для работы с пользователями:
- UserRead: для чтения данных пользователя (без пароля)
- UserCreate: для регистрации с защитой от критичных флагов
- UserUpdate: для обновления данных пользователя
"""
from typing import Any, ClassVar, Dict, Tuple

from fastapi_users import schemas
from pydantic import ConfigDict, model_validator


class UserRead(schemas.BaseUser[int]):
    """
    Схема для чтения данных пользователя (без пароля).

    Наследует базовую схему с целочисленным ID.
    """
    pass


class UserCreate(schemas.BaseUserCreate):
    """
    Схема для регистрации нового пользователя без критичных флагов.

    Содержит кастомный валидатор, который запрещает передачу флагов
    is_active, is_superuser, is_verified при регистрации.
    """
    # Запрещаем дополнительные поля в запросе
    model_config = ConfigDict(extra="forbid")

    # Критичные флаги, которые нельзя передавать при регистрации
    _admin_flags: ClassVar[Tuple[str, ...]] = (
        "is_active",
        "is_superuser",
        "is_verified"
    )

    @model_validator(mode="before")
    @classmethod
    def _reject_admin_flags(cls, data: Any) -> Any:
        """
        Валидатор, который проверяет, что клиент не пытается передать
        критические флаги при регистрации.

        Args:
            data: Входные данные от клиента.

        Returns:
            Оригинальные данные, если проверка пройдена.

        Raises:
            ValueError: Если обнаружены запрещённые поля.
        """
        if isinstance(data, dict):
            # Проверяем, есть ли запрещённые поля в данных
            forbidden = [field for field in cls._admin_flags if field in data]
            if forbidden:
                # Формируем сообщение об ошибке
                forbidden_str = ", ".join(forbidden)
                raise ValueError(
                    f"Недопустимые поля в регистрации: {forbidden_str}. "
                    "Управляющие флаги задаются только на сервере."
                )
        return data

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, model):
        """
        Удаляет критичные поля из JSON-схемы для документации OpenAPI.

        Это нужно, чтобы в Swagger UI не отображались поля, которые
        клиенту нельзя передавать.
        """
        # Удаляем запрещённые поля из списка свойств
        for field in cls._admin_flags:
            if field in schema.get("properties", {}):
                del schema["properties"][field]
            # Удаляем из списка обязательных полей
            if field in schema.get("required", []):
                schema["required"] = [
                    f for f in schema["required"] if f != field
                ]
        return schema


class UserUpdate(schemas.BaseUserUpdate):
    """
    Схема для обновления данных пользователя.
    """
    pass