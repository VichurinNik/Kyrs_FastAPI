from pydantic import BaseModel, Field, ConfigDict
from schemas.category import CategoryRead


class Product(BaseModel):
    id: int = Field(description="Уникальный идентификатор продукта")
    name: str = Field(max_length=100, description="Название продукта")
    description: str = Field(max_length=500, description="Описание продукта")
    image_url: str = Field(max_length=200, description="URL изображения продукта")
    price_shmeckles: float = Field(
        gt=0,
        description="Цена в шмекелях",
        example=19.99
    )
    price_flurbos: float = Field(
        gt=0,
        description="Цена в флурбо",
        example=14.50
    )
    price_credits: float = Field(
        gt=0,
        description="Цена в кредитах",
        example=9.80
    )
    category: CategoryRead = Field(description="Категория продукта")

    model_config = ConfigDict(from_attributes=True)