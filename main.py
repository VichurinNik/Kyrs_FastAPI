from fastapi import FastAPI, HTTPException, Path, Query
from typing import List, Optional
from data import products
from schemas.product import Product
from schemas.product_create import ProductCreate
from utils.helpers import get_next_id
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Вичурин Никита — Домашнее задание №32",
    description="REST API для интернет-магазина товаров из вселенной Рика и Морти",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Перенаправление на документацию"""
    return RedirectResponse(url="/docs")


@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools():
    """Заглушка для Chrome DevTools"""
    return {"message": "Chrome DevTools configuration"}


@app.get(
    "/products/",
    response_model=List[Product],
    status_code=200,
    summary="Получить все продукты с фильтрацией и сортировкой",
    tags=["Products"]
)
async def get_all_products(
        search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
        currency: Optional[str] = Query(None, description="Валюта для сортировки"),
        sort_order: Optional[str] = Query(None, description="Направление сортировки")
):
    filtered_products = products.copy()

    # Применяем поиск
    if search:
        search_lower = search.lower()
        filtered_products = [
            product for product in filtered_products
            if search_lower in product["name"].lower() or search_lower in product["description"].lower()
        ]

    # Применяем сортировку
    if currency and sort_order:
        def get_price(product):
            return product["prices"].get(currency, float('inf'))

        reverse = sort_order.lower() == "desc"
        filtered_products.sort(key=get_price, reverse=reverse)

    return filtered_products


@app.get(
    "/products/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Получить продукт по ID",
    tags=["Products"]
)
async def get_product(
        product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Получить информацию о конкретном продукте по его ID.

    - **product_id**: Уникальный идентификатор продукта (целое число >= 1)
    """
    product = next((p for p in products if p["id"] == product_id), None)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    return product


@app.post(
    "/products/",
    response_model=Product,
    status_code=201,
    summary="Создать новый продукт",
    tags=["Products"]
)
async def create_product(product_data: ProductCreate):
    """
    Создать новый продукт в магазине.

    Автоматически генерирует следующий доступный ID.
    Все поля обязательны для заполнения.
    """
    new_id = get_next_id()
    new_product = {
        "id": new_id,
        **product_data.model_dump()
    }
    products.append(new_product)
    return new_product


@app.put(
    "/products/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Обновить продукт",
    tags=["Products"]
)
async def update_product(
        product_id: int = Path(..., ge=1, description="ID продукта"),
        product_data: ProductCreate = ...
):
    """
    Полностью обновить информацию о продукте.

    - **product_id**: ID обновляемого продукта
    - **product_data**: Новые данные продукта (все поля обязательны)
    """
    # Находим индекс продукта
    product_index = next((i for i, p in enumerate(products) if p["id"] == product_id), None)

    if product_index is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    # Обновляем продукт, сохраняя старый ID
    updated_product = {
        "id": product_id,
        **product_data.model_dump()
    }
    products[product_index] = updated_product

    return updated_product


@app.delete(
    "/products/{product_id}",
    status_code=204,
    summary="Удалить продукт",
    tags=["Products"]
)
async def delete_product(
        product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Удалить продукт из магазина.

    - **product_id**: ID удаляемого продукта

    Возвращает статус 204 без содержимого при успешном удалении.
    """
    product_index = next((i for i, p in enumerate(products) if p["id"] == product_id), None)

    if product_index is None:
        raise HTTPException(
            status_code=404,
            detail=f"Продукт с ID {product_id} не найден"
        )

    products.pop(product_index)
    # Возвращаем None для статуса 204 (No Content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
