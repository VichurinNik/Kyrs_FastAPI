from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic import computed_field


# === Схемы для корзины ===

class CartItemCreate(BaseModel):
    """Схема для добавления товара в корзину"""
    product_id: int = Field(gt=0, description="ID товара")
    quantity: int = Field(ge=1, default=1, description="Количество товара")


class ProductInCart(BaseModel):
    """Схема товара для отображения в корзине"""
    id: int
    name: str
    description: str
    price_shmeckles: float
    price_flurbos: float
    price_credits: float
    image_url: Optional[str] = None
    category_id: int

    # Критически важно: остаток на складе
    quantity: int = Field(description="Остаток товара на складе")

    model_config = ConfigDict(from_attributes=True)


class CartItemRead(BaseModel):
    """Схема для отображения позиции в корзине"""
    id: int
    product_id: int
    quantity: int = Field(description="Количество в корзине")
    product: ProductInCart

    @computed_field
    @property
    def subtotal(self) -> float:
        """Сумма по позиции"""
        return self.product.price_shmeckles * self.quantity

    model_config = ConfigDict(from_attributes=True)


class CartRead(BaseModel):
    """Схема для отображения полной корзины"""
    id: int
    user_id: int
    items: List[CartItemRead]

    @computed_field
    @property
    def total_price(self) -> float:
        """Общая сумма корзины"""
        return sum(item.subtotal for item in self.items)

    @computed_field
    @property
    def total_items(self) -> int:
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items)

    model_config = ConfigDict(from_attributes=True)


# === Схемы для заказов ===

class OrderCreate(BaseModel):
    """Схема для создания заказа"""
    delivery_address: str = Field(
        min_length=10,
        max_length=500,
        description="Адрес доставки",
        example="г. Москва, ул. Пушкина, д. 10, кв. 25"
    )
    phone: str = Field(
        min_length=10,
        max_length=20,
        description="Контактный телефон",
        example="+7 (999) 123-45-67"
    )


class OrderItemRead(BaseModel):
    """Схема для отображения позиции заказа"""
    id: int
    product_id: int
    quantity: int
    frozen_name: str
    frozen_price: float

    @computed_field
    @property
    def subtotal(self) -> float:
        """Сумма по позиции (замороженная цена)"""
        return self.frozen_price * self.quantity

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    """Схема для отображения заказа"""
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_amount: float
    delivery_address: str
    phone: str
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)