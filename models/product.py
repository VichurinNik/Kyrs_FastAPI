from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional  # Уже импортирован

from models.base import Base


class Product(Base):
    """
    Модель товара
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Уже существует
    price_shmeckles: Mapped[float] = mapped_column(Float, nullable=False)
    price_flurbos: Mapped[float] = mapped_column(Float, nullable=False)
    price_credits: Mapped[float] = mapped_column(Float, nullable=False)

    # Внешний ключ для связи с категорией
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )

    # Обратная связь с категорией
    category: Mapped["Category"] = relationship(
        back_populates="products"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name}>"