from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import FastAPIUsers
import logging

from core.database import AsyncSessionLocal
from models.user import User
from models.commerce import Cart, CartItem, Order, OrderItem
from models.product import Product as ProductModel
from schemas.commerce import OrderCreate, OrderRead
from auth.auth import auth_backend
from auth.manager import get_user_manager
from utils.telegram import send_telegram_notification

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


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
        order_data: OrderCreate,
        background_tasks: BackgroundTasks,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Создать заказ из корзины пользователя
    """
    logger.info(f"Создание заказа для пользователя {user.id}")

    try:
        # === ШАГ 1: Получение корзины ===
        cart_query = select(Cart).where(Cart.user_id == user.id).options(
            selectinload(Cart.items).selectinload(CartItem.product)
        )
        cart_result = await db.execute(cart_query)
        cart = cart_result.scalar_one_or_none()

        if not cart or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Корзина пуста"
            )

        logger.info(f"В корзине пользователя {user.id} найдено {len(cart.items)} позиций")

        # === ШАГ 2: Повторная проверка остатков ===
        unavailable_items = []
        for cart_item in cart.items:
            if cart_item.product.quantity < cart_item.quantity:
                unavailable_items.append({
                    "product_id": cart_item.product.id,
                    "product_name": cart_item.product.name,
                    "requested": cart_item.quantity,
                    "available": cart_item.product.quantity
                })
                logger.error(
                    f"Недостаточно товара {cart_item.product.name}. "
                    f"Запрошено: {cart_item.quantity}, доступно: {cart_item.product.quantity}"
                )

        if unavailable_items:
            detail = "Недостаточно товаров на складе:\n"
            for item in unavailable_items:
                detail += f"• {item['product_name']}: запрошено {item['requested']} шт., доступно {item['available']} шт.\n"

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail.strip()
            )

        # === ШАГ 3: Списание со склада ===
        for cart_item in cart.items:
            product = cart_item.product
            new_quantity = product.quantity - cart_item.quantity

            # Обновляем остаток
            await db.execute(
                update(ProductModel)
                .where(ProductModel.id == product.id)
                .values(quantity=new_quantity)
            )
            logger.info(f"Списание {cart_item.quantity} шт. товара {product.name}. Остаток: {new_quantity}")

        # === ШАГ 4: Расчет итоговой суммы ===
        total_amount = 0
        for cart_item in cart.items:
            total_amount += cart_item.product.price_shmeckles * cart_item.quantity

        logger.info(f"Итоговая сумма заказа: {total_amount} шмеклей")

        # === ШАГ 5: Создание записи заказа ===
        order = Order(
            user_id=user.id,
            status="pending",
            total_amount=total_amount,
            delivery_address=order_data.delivery_address,
            phone=order_data.phone
        )
        db.add(order)
        await db.flush()  # Получаем ID заказа

        logger.info(f"Создан заказ ID={order.id}")

        # === ШАГ 6: Создание позиций заказа с заморозкой данных ===
        order_items = []
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                frozen_name=cart_item.product.name,
                frozen_price=cart_item.product.price_shmeckles
            )
            db.add(order_item)
            order_items.append(order_item)
            logger.info(
                f"Создана позиция заказа: {cart_item.product.name} "
                f"({cart_item.quantity} шт. по {cart_item.product.price_shmeckles} шмеклей)"
            )

        # === ШАГ 7: Очистка корзины ===
        # Удаляем все элементы корзины
        await db.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .delete()
        )
        logger.info(f"Корзина пользователя {user.id} очищена")

        # === ШАГ 8: Коммит транзакции ===
        await db.commit()
        logger.info(f"Транзакция заказа {order.id} успешно завершена")

        # === ШАГ 9: Отправка уведомления ===
        # Загружаем заказ с позициями для уведомления
        await db.refresh(order, ["items"])

        # Формируем сообщение для Telegram
        message = f"""🛒 *Создан новый заказ!*

🆔 *Номер заказа:* {order.id}
👤 *Пользователь:* {user.email}
📦 *Количество позиций:* {len(order_items)}
💰 *Сумма заказа:* {total_amount:.2f} шмеклей
📅 *Дата создания:* {order.created_at.strftime('%d.%m.%Y %H:%M')}

🏠 *Адрес доставки:*
{order.delivery_address}

📞 *Контактный телефон:*
{order.phone}

📋 *Состав заказа:*
"""

        for item in order_items:
            message += f"• {item.frozen_name}: {item.quantity} шт. × {item.frozen_price} шмеклей = {item.quantity * item.frozen_price:.2f} шмеклей\n"

        # Добавляем фоновую задачу отправки уведомления
        background_tasks.add_task(send_telegram_notification, message)

        # Возвращаем созданный заказ
        return order

    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        logger.error(f"Ошибка при создании заказа: {e}")
        # Автоматический откат транзакции (не вызываем commit)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла ошибка при создании заказа"
        )


@router.get("/", response_model=list[OrderRead])
async def get_orders(
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Получить историю заказов текущего пользователя
    """
    logger.info(f"Получение истории заказов пользователя {user.id}")

    query = select(Order).where(
        Order.user_id == user.id
    ).options(
        selectinload(Order.items)
    ).order_by(
        Order.created_at.desc()
    )

    result = await db.execute(query)
    orders = result.scalars().all()

    logger.info(f"Найдено {len(orders)} заказов для пользователя {user.id}")

    return orders


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
        order_id: int,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Получить детали конкретного заказа
    """
    logger.info(f"Получение деталей заказа {order_id} для пользователя {user.id}")

    query = select(Order).where(
        Order.id == order_id,
        Order.user_id == user.id
    ).options(
        selectinload(Order.items)
    )

    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        logger.error(f"Заказ {order_id} не найден для пользователя {user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден"
        )

    return order