from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional

from schemas.product import Product
from schemas.product_create import ProductCreate
from data.products import products
from utils.helpers import get_next_id

# Создаем роутер с префиксом и тегом
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get(
    "/",
    response_model=List[Product],
    status_code=200,
    summary="Получить все продукты с фильтрацией и сортировкой"
)
async def get_all_products(
        search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
        currency: Optional[str] = Query(None, description="Валюта для сортировки (shmeckles, credits, flurbos)"),
        sort_order: Optional[str] = Query(None, description="Направление сортировки (asc, desc)")
):
    """
    Получить список всех товаров с возможностью поиска и сортировки.
    """
    filtered_products = products.copy()

    if search:
        search_lower = search.lower()
        filtered_products = [
            product for product in filtered_products
            if search_lower in product["name"].lower() or search_lower in product["description"].lower()
        ]

    if currency and sort_order:
        def get_price(product):
            return product["prices"].get(currency, float('inf'))

        reverse = sort_order.lower() == "desc"
        filtered_products.sort(key=get_price, reverse=reverse)

    return filtered_products


@router.get(
    "/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Получить продукт по ID"
)
async def get_product(
        product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Получить информацию о конкретном продукте по его ID.
    """
    product = next((p for p in products if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    return product


@router.post(
    "/",
    response_model=Product,
    status_code=201,
    summary="Создать новый продукт"
)
async def create_product(product_data: ProductCreate):
    """
    Создать новый продукт в магазине.
    """
    new_id = get_next_id()
    new_product = {
        "id": new_id,
        **product_data.model_dump()
    }
    products.append(new_product)
    return new_product


@router.put(
    "/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Обновить продукт"
)
async def update_product(
        product_id: int = Path(..., ge=1, description="ID продукта"),
        product_data: ProductCreate = ...
):
    """
    Полностью обновить информацию о продукте.
    """
    product_index = next((i for i, p in enumerate(products) if p["id"] == product_id), None)

    if product_index is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    updated_product = {
        "id": product_id,
        **product_data.model_dump()
    }
    products[product_index] = updated_product

    return updated_product


@router.delete(
    "/{product_id}",
    status_code=204,
    summary="Удалить продукт"
)
async def delete_product(
        product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Удалить продукт из магазина.
    """
    product_index = next((i for i, p in enumerate(products) if p["id"] == product_id), None)

    if product_index is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    products.pop(product_index)