from fastapi_shop.data.products import products  # Измененный импорт

def get_next_id() -> int:
    """Генерирует следующий доступный ID для нового продукта"""
    if not products:
        return 1
    max_id = max(product["id"] for product in products)
    return max_id + 1