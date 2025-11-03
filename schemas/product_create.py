from pydantic import BaseModel
from pydantic import Field
from typing import Dict


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Product Name",
                      examples=["Стандартный Плюмбус", "Коробка с Мисиксами"])
    description: str = Field(..., min_length=5, description="Product Description", examples=[
        "Каждый дом должен иметь плюмбус. Мы не знаем, что он делает, но он делает это очень хорошо.",
        "Нужна помощь по дому? Нажмите кнопку, и появится Мисикс, готовый выполнить одно ваше поручение."
    ])
    prices: Dict[str, float] = Field(..., description="Product Price",
                                     examples=[{"shmeckles": 6.5, "credits": 4.8, "flurbos": 3.2}])
    image_url: str = Field(..., description="Путь к изображению товара",
                           examples=["/images/plumbus.webp", "/images/meeseeks-box.webp"])
