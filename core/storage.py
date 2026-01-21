import logging
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

# Настройка логгера
logger = logging.getLogger(__name__)

# Константы
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Создаём папку, если её нет

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ


async def save_product_image(file: UploadFile) -> str:
    """
    Сохраняет изображение товара на сервер

    Args:
        file: Загружаемый файл

    Returns:
        URL-путь к сохранённому изображению

    Raises:
        HTTPException: Если файл невалиден
    """
    logger.info(f"📥 Начало загрузки файла: {file.filename}")

    # Проверка расширения файла
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.error(f"❌ Запрещённый формат файла: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат файла. Разрешённые форматы: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Чтение содержимого файла
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"❌ Ошибка чтения файла: {e}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось прочитать файл"
        )

    # Проверка размера файла
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        logger.error(f"❌ Файл слишком большой: {file_size} байт (максимум: {MAX_FILE_SIZE})")
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024 * 1024)} МБ"
        )

    # Генерация уникального имени файла
    filename = f"{uuid.uuid4()}{file_ext}"
    filepath = UPLOAD_DIR / filename

    # Сохранение файла
    try:
        with open(filepath, "wb") as f:
            f.write(content)
        logger.info(f"✅ Файл сохранён: {filepath}")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения файла: {e}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось сохранить файл"
        )

    # Формирование URL-пути
    image_url = f"/uploads/products/{filename}"
    return image_url


def delete_product_image(image_url: str) -> bool:
    """
    Удаляет изображение товара с сервера

    Args:
        image_url: URL изображения для удаления

    Returns:
        True если файл удалён, False если файла не существует
    """
    try:
        # Извлечение имени файла из URL
        filename = Path(image_url).name
        filepath = UPLOAD_DIR / filename

        # Проверка существования файла
        if not filepath.exists():
            logger.warning(f"⚠️ Файл для удаления не существует: {filepath}")
            return False

        # Удаление файла
        filepath.unlink()
        logger.info(f"🗑️ Файл удалён: {filepath}")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка удаления файла {image_url}: {e}")
        return False