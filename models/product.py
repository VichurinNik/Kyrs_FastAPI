from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from models.base import Base


class Product(Base):
    """
    Модель товара
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    price_shmeckles: Mapped[float] = mapped_column(Float, nullable=False)
    price_flurbos: Mapped[float] = mapped_column(Float, nullable=False)
    price_credits: Mapped[float] = mapped_column(Float, nullable=False)

    # Остаток на складе
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="10",
        comment="Остаток товара на складе"
    )

    # Внешний ключ для связи с категорией
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )

    # Обратная связь с категорией
    category: Mapped["Category"] = relationship(
        back_populates="products"
    )

    # Обратная связь с элементами корзины
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name} quantity={self.quantity}>"