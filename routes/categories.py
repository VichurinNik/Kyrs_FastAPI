from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from models.category import Category as CategoryModel
from schemas.category import CategoryCreate, CategoryRead

router = APIRouter(
    prefix="/categories",
    tags=["Категории"]
)


# Зависимость для получения сессии БД
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(
        category_data: CategoryCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Создать новую категорию
    """
    # Проверяем, существует ли категория с таким названием
    query = select(CategoryModel).where(CategoryModel.name == category_data.name)
    result = await db.execute(query)
    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail=f"Категория с названием '{category_data.name}' уже существует"
        )

    # Создаем новую категорию
    new_category = CategoryModel(name=category_data.name)

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category


@router.get("/", response_model=list[CategoryRead])
async def get_categories(
        search: str = None,
        db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех категорий
    """
    query = select(CategoryModel)

    # Применяем фильтрацию по поиску
    if search:
        query = query.where(CategoryModel.name.ilike(f"%{search}%"))

    # Сортировка по названию
    query = query.order_by(CategoryModel.name)

    result = await db.execute(query)
    categories = result.scalars().all()

    return categories


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
        category_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Получить категорию по ID
    """
    category = await db.get(CategoryModel, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {category_id} не найдена"
        )

    return category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
        category_id: int,
        category_data: CategoryCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Обновить категорию по ID
    """
    # Получаем категорию из БД
    category = await db.get(CategoryModel, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {category_id} не найдена"
        )

    # Проверяем, не существует ли другая категория с таким названием
    query = select(CategoryModel).where(
        CategoryModel.name == category_data.name,
        CategoryModel.id != category_id
    )
    result = await db.execute(query)
    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail=f"Категория с названием '{category_data.name}' уже существует"
        )

    # Обновляем название категории
    category.name = category_data.name

    await db.commit()
    await db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(
        category_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Удалить категорию по ID
    """
    # Получаем категорию из БД
    category = await db.get(CategoryModel, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {category_id} не найдена"
        )

    # Удаляем категорию
    await db.delete(category)
    await db.commit()

    return None


@router.get("/{category_id}/products", response_model=list[CategoryRead])
async def get_category_products(
        category_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    Получить все продукты категории
    """
    category = await db.get(CategoryModel, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {category_id} не найдена"
        )

    return category