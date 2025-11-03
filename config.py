from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения"""

    tg_bot_key: str = Field(
        ...,
        description="API ключ для Telegram бота",
        examples=["1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567"]
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаем экземпляр настроек
settings = Settings()