from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.product import Product as ProductModel
from models.category import Category as CategoryModel  # НОВЫЙ ИМПОРТ
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
        category_id: int = None,  # НОВЫЙ ПАРАМЕТР
        db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех продуктов с возможностью фильтрации и сортировки
    """
    # Используем "жадную" загрузку для связанной категории
    query = select(ProductModel).options(selectinload(ProductModel.category))

    # Применяем фильтрацию по поиску
    if search:
        query = query.where(
            or_(
                ProductModel.name.ilike(f"%{search}%"),
                ProductModel.description.ilike(f"%{search}%")
            )
        )

    # Фильтрация по категории
    if category_id:
        query = query.where(ProductModel.category_id == category_id)

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
    # Используем "жадную" загрузку для связанной категории
    query = select(ProductModel).options(selectinload(ProductModel.category))
    query = query.where(ProductModel.id == product_id)

    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    return product


@router.post("/", response_model=ProductSchema)
async def create_product(
        product_data: ProductCreate,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    """
    Создать новый продукт
    """
    # Проверяем существование категории
    category = await db.get(CategoryModel, product_data.category_id)
    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {product_data.category_id} не найдена"
        )

    # Создаем новый продукт
    new_product = ProductModel(**product_data.model_dump())

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    # Загружаем связанную категорию для ответа
    await db.refresh(new_product, ["category"])

    # Формируем сообщение для Telegram
    message = f"""🆕 *Создан новый продукт*

📦 *Название:* {new_product.name}
🆔 *ID:* {new_product.id}
📝 *Описание:* {new_product.description[:100]}...
🏷️ *Категория:* {category.name}

💰 *Цены:*
  • Шмекели: {new_product.price_shmeckles}
  • Флурбо: {new_product.price_flurbos}
  • Кредиты: {new_product.price_credits}
"""

    background_tasks.add_task(send_telegram_notification, message)

    return new_product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
        product_id: int,
        product_data: ProductCreate,
        background_tasks: BackgroundTasks,
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

    # Проверяем существование новой категории
    if product_data.category_id != product.category_id:
        category = await db.get(CategoryModel, product_data.category_id)
        if category is None:
            raise HTTPException(
                status_code=404,
                detail=f"Категория с ID {product_data.category_id} не найдена"
            )

    # Сохраняем старые данные для уведомления
    old_name = product.name
    old_category_id = product.category_id

    # Обновляем поля продукта
    for field, value in product_data.model_dump().items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    # Загружаем связанную категорию для ответа
    await db.refresh(product, ["category"])

    # Формируем сообщение для Telegram
    category = await db.get(CategoryModel, product_data.category_id)
    message = f"""✏️ *Обновлен продукт*

📦 *Название:* {old_name} → {product.name}
🆔 *ID:* {product_id}
📝 *Описание обновлено*

{"🏷️ *Категория изменена*" if old_category_id != product_data.category_id else "🏷️ *Категория:*"} {category.name}

💰 *Новые цены:*
  • Шмекели: {product.price_shmeckles}
  • Флурбо: {product.price_flurbos}
  • Кредиты: {product.price_credits}
"""

    background_tasks.add_task(send_telegram_notification, message)

    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
        product_id: int,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
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

    # Сохраняем информацию для уведомления
    product_name = product.name
    category = await db.get(CategoryModel, product.category_id)
    category_name = category.name if category else "Неизвестная категория"

    await db.delete(product)
    await db.commit()

    # Формируем сообщение для Telegram
    message = f"""🗑️ *Удален продукт*

📦 *Название:* {product_name}
🆔 *ID:* {product_id}
🏷️ *Категория:* {category_name}
"""

    background_tasks.add_task(send_telegram_notification, message)

    return None