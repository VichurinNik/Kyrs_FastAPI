from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import FastAPIUsers
import logging

from core.database import AsyncSessionLocal
from models.user import User
from models.commerce import Cart, CartItem
from models.product import Product as ProductModel
from schemas.commerce import (
    CartItemCreate,
    CartRead,
    CartItemRead,
    ProductInCart
)
from auth.auth import auth_backend
from auth.manager import get_user_manager

logger = logging.getLogger(__name__)

router = APIRouter()
fastapi_users = FastAPIUsers[User, str](
    get_user_manager,
    [auth_backend],
)


# Зависимости
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


current_user = fastapi_users.current_user()


@router.get("/", response_model=CartRead)
async def get_cart(
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Получить корзину текущего пользователя
    """
    logger.info(f"Получение корзины для пользователя {user.id}")

    # Поиск или создание корзины
    query = select(Cart).where(Cart.user_id == user.id).options(
        selectinload(Cart.items).selectinload(CartItem.product)
    )
    result = await db.execute(query)
    cart = result.scalar_one_or_none()

    if not cart:
        logger.info(f"Создание новой корзины для пользователя {user.id}")
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    return cart


@router.post("/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
        item_data: CartItemCreate,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Добавить товар в корзину
    """
    logger.info(f"Добавление товара {item_data.product_id} в корзину пользователя {user.id}")

    # 1. Проверка существования товара
    product_query = select(ProductModel).where(ProductModel.id == item_data.product_id)
    product_result = await db.execute(product_query)
    product = product_result.scalar_one_or_none()

    if not product:
        logger.error(f"Товар {item_data.product_id} не найден")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар с ID {item_data.product_id} не найден"
        )

    # 2. Проверка остатка на складе
    if product.quantity < item_data.quantity:
        logger.error(
            f"Недостаточно товара {product.name}. Запрошено: {item_data.quantity}, доступно: {product.quantity}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недостаточно товара '{product.name}' на складе. Доступно: {product.quantity} шт."
        )

    # 3. Получение корзины
    cart_query = select(Cart).where(Cart.user_id == user.id).options(
        selectinload(Cart.items)
    )
    cart_result = await db.execute(cart_query)
    cart = cart_result.scalar_one_or_none()

    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.flush()

    # 4. Проверка, есть ли товар уже в корзине
    existing_item = None
    for cart_item in cart.items:
        if cart_item.product_id == item_data.product_id:
            existing_item = cart_item
            break

    if existing_item:
        # Проверка суммарного количества
        total_quantity = existing_item.quantity + item_data.quantity
        if total_quantity > product.quantity:
            logger.error(
                f"Недостаточно товара для добавления. Уже в корзине: {existing_item.quantity}, запрошено: {item_data.quantity}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Нельзя добавить {item_data.quantity} шт. товара '{product.name}'. "
                    f"Уже в корзине: {existing_item.quantity} шт. "
                    f"Всего доступно: {product.quantity} шт."
                )
            )

        existing_item.quantity = total_quantity
        logger.info(f"Увеличение количества товара {product.name} в корзине до {total_quantity}")
    else:
        # Создание нового элемента корзины
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(new_item)
        logger.info(f"Добавление товара {product.name} в корзину, количество: {item_data.quantity}")

    await db.commit()

    # 5. Возвращаем обновленную корзину
    await db.refresh(cart, ["items"])
    for item in cart.items:
        await db.refresh(item, ["product"])

    return cart


@router.delete("/items/{item_id}", response_model=CartRead)
async def remove_from_cart(
        item_id: int,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Удалить товар из корзины
    """
    logger.info(f"Удаление товара {item_id} из корзины пользователя {user.id}")

    # Находим корзину пользователя
    cart_query = select(Cart).where(Cart.user_id == user.id)
    cart_result = await db.execute(cart_query)
    cart = cart_result.scalar_one_or_none()

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Корзина не найдена"
        )

    # Находим элемент корзины
    item_query = select(CartItem).where(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    )
    item_result = await db.execute(item_query)
    item = item_result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар с ID {item_id} не найден в корзине"
        )

    # Удаляем элемент
    await db.delete(item)
    await db.commit()

    logger.info(f"Товар {item_id} удален из корзины")

    # Возвращаем обновленную корзину
    await db.refresh(cart, ["items"])
    for item in cart.items:
        await db.refresh(item, ["product"])

    return cart


@router.delete("/", response_model=CartRead)
async def clear_cart(
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Очистить корзину
    """
    logger.info(f"Очистка корзины пользователя {user.id}")

    # Находим корзину пользователя
    cart_query = select(Cart).where(Cart.user_id == user.id)
    cart_result = await db.execute(cart_query)
    cart = cart_result.scalar_one_or_none()

    if not cart:
        # Если корзины нет, создаем пустую
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        return cart

    # Удаляем все элементы корзины
    items_query = select(CartItem).where(CartItem.cart_id == cart.id)
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    for item in items:
        await db.delete(item)

    await db.commit()
    logger.info(f"Корзина пользователя {user.id} очищена")

    return cart