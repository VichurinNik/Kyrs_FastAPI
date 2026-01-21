from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile
from sqlalchemy import select, or_, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.product import Product as ProductModel
from models.category import Category as CategoryModel
from schemas.product import Product as ProductSchema
from schemas.product_create import ProductCreate
from utils.telegram import send_telegram_notification
from core.storage import save_product_image, delete_product_image  # НОВЫЕ ИМПОРТЫ
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Зависимость для получения сессии БД
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# Вспомогательная функция для получения товара по ID
async def product_get_by_id(session: AsyncSession, product_id: int):
    """
    Получить товар по ID
    """
    query = select(ProductModel).options(selectinload(ProductModel.category))
    query = query.where(ProductModel.id == product_id)

    result = await session.execute(query)
    product = result.scalar_one_or_none()

    return product


# ... остальные существующие эндпоинты ...


@router.post("/{product_id}/upload-image", summary="Загрузить изображение для товара")
async def upload_product_image(
        product_id: int,
        file: UploadFile,
        db: AsyncSession = Depends(get_db)
):
    """
    Загружает изображение для товара и привязывает его.
    Если старое изображение было — оно удаляется.
    """
    logger.info(f"📥 Запрос на загрузку изображения для товара ID={product_id}")

    # Проверка существования товара
    product = await product_get_by_id(db, product_id)
    if product is None:
        logger.error(f"❌ Товар с ID={product_id} не найден")
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {product_id} не найден"
        )

    # Удаление старого изображения, если оно есть
    if product.image_url:
        logger.info(f"🗑️ Удаление старого изображения: {product.image_url}")
        delete_product_image(product.image_url)

    # Сохранение нового изображения
    try:
        image_url = await save_product_image(file)
    except HTTPException as e:
        logger.error(f"❌ Ошибка загрузки изображения: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка загрузки изображения: {e}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось загрузить изображение"
        )

    # Обновление URL в базе данных
    try:
        stmt = update(ProductModel).where(
            ProductModel.id == product_id
        ).values(image_url=image_url)

        await db.execute(stmt)
        await db.commit()

        logger.info(f"✅ Изображение обновлено для товара ID={product_id}: {image_url}")

    except Exception as e:
        logger.error(f"❌ Ошибка обновления БД для товара ID={product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось обновить товар в базе данных"
        )

    return {
        "product_id": product_id,
        "image_url": image_url,
        "message": "Изображение успешно загружено"
    }


@router.delete("/{product_id}/image", summary="Удалить изображение товара")
async def delete_product_image_endpoint(
        product_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Удаляет изображение товара (с диска и из БД).
    """
    logger.info(f"🗑️ Запрос на удаление изображения для товара ID={product_id}")

    # Получение товара
    product = await product_get_by_id(db, product_id)
    if product is None:
        logger.error(f"❌ Товар с ID={product_id} не найден")
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {product_id} не найден"
        )

    # Проверка наличия изображения
    if not product.image_url:
        logger.error(f"❌ У товара ID={product_id} нет изображения")
        raise HTTPException(
            status_code=400,
            detail=f"У товара с ID {product_id} нет изображения"
        )

    # Удаление файла с диска
    if not delete_product_image(product.image_url):
        logger.warning(f"⚠️ Файл изображения не найден на диске: {product.image_url}")

    # Обновление БД
    try:
        stmt = update(ProductModel).where(
            ProductModel.id == product_id
        ).values(image_url=None)

        await db.execute(stmt)
        await db.commit()

        logger.info(f"✅ Изображение удалено для товара ID={product_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка обновления БД для товара ID={product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось обновить товар в базе данных"
        )

    return {
        "message": "Изображение успешно удалено",
        "product_id": product_id
    }

