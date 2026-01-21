import asyncio
from core.database import AsyncSessionLocal, init_db
from models.product import Product


async def seed_database():
    """
    Заполнение базы данных тестовыми продуктами
    """
    # Инициализируем БД (создаем таблицы)
    await init_db()

    # Тестовые продукты (адаптированные под новую структуру)
    products_data = [
        {
            "name": "Стандартный Плюмбус",
            "description": "Каждый дом должен иметь плюмбус. Мы не знаем, что он делает, но он делает это очень хорошо.",
            "image_url": "/images/plumbus.webp",
            "price_shmeckles": 6.5,
            "price_credits": 4.8,
            "price_flurbos": 3.2,
        },
        {
            "name": "Коробка с Мисиксами",
            "description": "Нужна помощь по дому? Нажмите кнопку, и появится Мисикс, готовый выполнить одно ваше поручение.",
            "image_url": "/images/meeseeks-box.webp",
            "price_shmeckles": 19.99,
            "price_credits": 14.5,
            "price_flurbos": 9.8,
        },
        {
            "name": "Портальная пушка (б/у)",
            "description": "Слегка поцарапана, заряд портальной жидкости на 37%. Возврату не подлежит.",
            "image_url": "/images/portal-gun.webp",
            "price_shmeckles": 9999.99,
            "price_credits": 7500.0,
            "price_flurbos": 4999.99,
        },
        {
            "name": "Межгалактический Кабельный Канал",
            "description": "Смотрите телевизор во всех 600 каналах всех измерений одновременно. Батарейки не входят в комплект.",
            "image_url": "/images/intergalactic-cable.webp",
            "price_shmeckles": 299.99,
            "price_credits": 225.0,
            "price_flurbos": 149.99,
        },
        {
            "name": "Концентрат темной материи",
            "description": "Для тех, кто хочет создать свою собственную вселенную. Инструкция прилагается.",
            "image_url": "/images/dark-matter.webp",
            "price_shmeckles": 4999.99,
            "price_credits": 3750.0,
            "price_flurbos": 2499.99,
        },
        {
            "name": "Микро-верстак",
            "description": "Идеальный подарок для инженера-изобретателя. Помещается в карман.",
            "image_url": "/images/micro-versatak.webp",
            "price_shmeckles": 89.99,
            "price_credits": 67.5,
            "price_flurbos": 44.99,
        },
        {
            "name": "Бутылка с портальной жидкостью",
            "description": "Зарядите вашу портальную пушку. Только для лицензированных пользователей.",
            "image_url": "/images/portal-fluid.webp",
            "price_shmeckles": 149.99,
            "price_credits": 112.5,
            "price_flurbos": 74.99,
        }
    ]

    async with AsyncSessionLocal() as session:
        for product_data in products_data:
            product = Product(**product_data)
            session.add(product)

        await session.commit()
        print(f"Добавлено {len(products_data)} продуктов в базу данных")


if __name__ == "__main__":
    asyncio.run(seed_database())