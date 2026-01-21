from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """
    Схема для создания категории
    """
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Название категории",
        example="Электроника"
    )


class CategoryRead(BaseModel):
    """
    Схема для чтения категории
    """
    id: int = Field(description="Уникальный идентификатор категории")
    name: str = Field(description="Название категории")

    model_config = ConfigDict(from_attributes=True)