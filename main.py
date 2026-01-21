# ... существующие импорты ...
from routes import cart, orders

app = FastAPI(
    title="FastAPI Shop",
    description="Магазин товаров из мультсериала Rick and Morty",
    version="1.0.0",
    lifespan=lifespan
)

# ... существующие роутеры ...

# Подключаем роутеры корзины и заказов
app.include_router(
    cart.router,
    prefix="/cart",
    tags=["Корзина"]
)

app.include_router(
    orders.router,
    prefix="/orders",
    tags=["Заказы"]
)