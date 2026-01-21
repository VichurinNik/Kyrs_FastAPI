from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.product import Product as ProductModel
from schemas.product import Product as ProductSchema
from schemas.product_create import ProductCreate
from utils.telegram import send_telegram_notification

router = APIRouter()


# Зависимость для получения сессии БД
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/", response_model=list[ProductSchema])
async def get_products(
        search: str = None,
        currency: str = None,
        sort_order: str = "asc",
        db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех продуктов с возможностью фильтрации и сортировки
    """
    query = select(ProductModel)

    # Применяем фильтрацию по поиску
    if search:
        query = query.where(
            or_(
                ProductModel.name.ilike(f"%{search}%"),
                ProductModel.description.ilike(f"%{search}%")
            )
        )

    # Применяем сортировку по валюте
    if currency:
        try:
            price_column = getattr(ProductModel, f"price_{currency}")
            if sort_order.lower() == "desc":
                query = query.order_by(price_column.desc())
            else:
                query = query.order_by(price_column)
        except AttributeError:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимая валюта: {currency}. Допустимые значения: shmeckles, flurbos, credits"
            )

    result = await db.execute(query)
    products = result.scalars().all()

    return products


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить продукт по ID
    """
    product = await db.get(ProductModel, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    return product


@router.post("/", response_model=ProductSchema)
async def create_product(
        product_data: ProductCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Создать новый продукт
    """
    # Создаем новый продукт из данных
    new_product = ProductModel(**product_data.model_dump())

    # Добавляем в сессию и сохраняем в БД
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    # Формируем сообщение для Telegram
    message = f"""🆕 *Создан новый продукт*

📦 *Название:* {new_product.name}
🆔 *ID:* {new_product.id}
📝 *Описание:* {new_product.description[:100]}...

💰 *Цены:*
  • Шмекели: {new_product.price_shmeckles}
  • Флурбо: {new_product.price_flurbos}
  • Кредиты: {new_product.price_credits}
"""

    # Отправляем уведомление в фоновом режиме
    await send_telegram_notification(message)

    return new_product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
        product_id: int,
        product_data: ProductCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Обновить продукт по ID
    """
    # Получаем продукт из БД
    product = await db.get(ProductModel, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    # Обновляем поля продукта
    for field, value in product_data.model_dump().items():
        setattr(product, field, value)

    # Сохраняем изменения
    await db.commit()
    await db.refresh(product)

    # Формируем сообщение для Telegram
    message = f"""✏️ *Обновлен продукт*

📦 *Название:* {product.name}
🆔 *ID:* {product.id}
📝 *Описание:* {product.description[:100]}...

💰 *Новые цены:*
  • Шмекели: {product.price_shmeckles}
  • Флурбо: {product.price_flurbos}
  • Кредиты: {product.price_credits}
"""

    # Отправляем уведомление в фоновом режиме
    await send_telegram_notification(message)

    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить продукт по ID
    """
    # Получаем продукт из БД
    product = await db.get(ProductModel, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    # Удаляем продукт
    await db.delete(product)
    await db.commit()

    # Формируем сообщение для Telegram
    message = f"""🗑️ *Удален продукт*

📦 *Название:* {product.name}
🆔 *ID:* {product.id}
"""

    # Отправляем уведомление в фоновом режиме
    await send_telegram_notification(message)

    return None