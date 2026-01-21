"""
Скрипт для наполнения базы данных тестовыми данными
"""
import asyncio
from core.database import AsyncSessionLocal
from models.product import Product
from models.category import Category

# Данные из задания
CATEGORIES = [
    {"name": "Технологии", "description": "Высокотехнологичные устройства"},
    {"name": "Бытовые приборы", "description": "Для дома и быта"},
    {"name": "Топливо и энергия", "description": "Источники энергии"},
    {"name": "Развлечения", "description": "Игры и симуляторы"},
    {"name": "Продукты питания", "description": "Еда и напитки"},
    {"name": "Медицина", "description": "Лекарства и медтехника"},
    {"name": "Транспорт", "description": "Средства передвижения"},
    {"name": "Оружие", "description": "Боевые устройства"},
]

TAGS = [
    "Популярное",
    "Опасно",
    "Научная фантастика",
    "Юмор",
    "Экзистенциальный кризис",
    "Межпространственное",
    "Новинка",
    "Распродажа",
    "Незаконно",
    "Гарантия не распространяется",
]

# Курс конвертации: 1 Шмекель = 2 Флёрбо
SHMECKLES_TO_FLURBOS = 2.0

PRODUCTS = [
    {
        "name": "Стандартный Плюмбус",
        "description": "Каждый дом должен иметь плюмбус. Мы не знаем, что он делает, но он делает это очень хорошо. В комплекте: шлее, грумбо и флиб.",
        "price_shmeckles": 6.5,
        "image": "plumbus.webp",
        "category": "Бытовые приборы",
        "tags": ["Популярное", "Юмор"],
    },
    # ... все остальные продукты из задания ...
]


async def seed_database(clear: bool = False):
    """
    Заполнение базы данных тестовыми данными
    """
    from sqlalchemy import delete

    async with AsyncSessionLocal() as session:
        if clear:
            # Очистка таблиц
            await session.execute(delete(Product))
            await session.execute(delete(Category))
            await session.commit()
            print("✅ Таблицы очищены")

        # Создание категорий
        category_map = {}
        for cat_data in CATEGORIES:
            category = Category(**cat_data)
            session.add(category)
            await session.flush()
            category_map[cat_data["name"]] = category.id

        await session.commit()
        print(f"✅ Добавлено {len(CATEGORIES)} категорий")

        # Создание продуктов
        for i, prod_data in enumerate(PRODUCTS, 1):
            product = Product(
                name=prod_data["name"],
                description=prod_data["description"],
                image_url=f"/images/{prod_data['image']}" if 'image' in prod_data else None,
                price_shmeckles=prod_data["price_shmeckles"],
                price_flurbos=prod_data["price_shmeckles"] * SHMECKLES_TO_FLURBOS,
                price_credits=prod_data["price_shmeckles"] * 0.75,
                category_id=category_map[prod_data["category"]]
            )
            session.add(product)

        await session.commit()
        print(f"✅ Добавлено {len(PRODUCTS)} продуктов")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Заполнение базы данных тестовыми данными")
    parser.add_argument("--clear", action="store_true", help="Очистить таблицы перед заполнением")

    args = parser.parse_args()

    asyncio.run(seed_database(clear=args.clear))