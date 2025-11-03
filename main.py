from fastapi import FastAPI
from typing import List
from data import products
from schemas.product import Product

app = FastAPI(
    title="Вичурин Никита — Домашнее задание №31",
    description="REST API для интернет-магазина товаров из вселенной Рика и Морти",
    version="1.0.0"
)

@app.get(
    "/products/",
    response_model=List[Product],
    status_code=200,
    summary="Получить все продукты",
    tags=["Products"]
)
async def get_all_products():
    """
    Получить полный список всех товаров из магазина.
    Возвращает массив объектов Product с информацией о каждом товаре,
    включая название, описание, цены в разных валютах и ссылку на изображение.
    """
    return products

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
