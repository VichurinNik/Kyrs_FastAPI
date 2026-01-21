from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    telegram_bot_api_key: str = Field(
        ...,
        description="API ключ для бота Telegram"
    )

    telegram_user_id: str = Field(
        ...,
        description="ID пользователя Telegram для отправки уведомлений"
    )

    database_url: str = Field(
        ...,
        description="URL для подключения к базе данных"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()