import httpx
from core.config import settings


async def send_telegram_notification(message: str):
    """
    Отправка уведомления в Telegram
    """
    url = f"https://api.telegram.org/bot{settings.telegram_bot_api_key}/sendMessage"

    payload = {
        "chat_id": settings.telegram_user_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Ошибка отправки уведомления в Telegram: {e}")