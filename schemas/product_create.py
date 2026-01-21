from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Название продукта"
    )
    description: str = Field(
        min_length=1,
        max_length=500,
        description="Описание продукта"
    )
    image_url: str = Field(
        min_length=1,
        max_length=200,
        description="URL изображения продукта"
    )
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