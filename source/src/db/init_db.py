import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.db.database import engine, SessionLocal
from src.db.models import Base, User, Product, Order, PickupPoint, order_product
from src.utils.security import get_password_hash


def create_tables():
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы успешно!")


def load_users(db: Session):
    print("Загрузка пользователей...")

    users_data = [
        {"role": "Администратор", "full_name": "Администратор", "login": "admin", "password": "admin"},
        {"role": "Менеджер", "full_name": "Борсин Пётр Евгеньевич", "login": "manager", "password": "manager"},
        {"role": "авторизованный клиент", "full_name": "Михайлюк Анна Вячеславовна", "login": "client",
         "password": "client"},
    ]

    for user_data in users_data:
        existing = db.query(User).filter(User.login == user_data["login"]).first()
        if not existing:
            user = User(
                role=user_data["role"],
                full_name=user_data["full_name"],
                login=user_data["login"],
                password=get_password_hash(user_data["password"])
            )
            db.add(user)

    db.commit()
    print(f"Загружено пользователей: {len(users_data)}")


def load_pickup_points(db: Session):
    print("Загрузка пунктов выдачи...")

    addresses = [
        "420151, г. Лесной, ул. Вишневая, 32",
        "125061, г. Лесной, ул. Подгорная, 8",
        "630370, г. Лесной, ул. Шоссейная, 24",
        "400562, г. Лесной, ул. Зеленая, 32",
        "614510, г. Лесной, ул. Маяковского, 47",
    ]

    for address in addresses:
        existing = db.query(PickupPoint).filter(PickupPoint.address == address).first()
        if not existing:
            point = PickupPoint(address=address)
            db.add(point)

    db.commit()
    print(f"Загружено пунктов выдачи: {len(addresses)}")


def load_products(db: Session):
    print("Загрузка товаров...")

    products_data = [
        {
            "article": "A11214",
            "name": "Ботинки",
            "unit": "шт.",
            "price": 4990,
            "supplier": "Karl",
            "manufacturer": "Karl",
            "category": "Женская обувь",
            "discount": 3,
            "quantity": 6,
            "description": "Женские ботинки демисезонные karl",
            "photo": None
        },
        {
            "article": "F6358R4",
            "name": "Ботинки",
            "unit": "шт.",
            "price": 3244,
            "supplier": "Обувь для вас",
            "manufacturer": "Marco Tozzi",
            "category": "Женская обувь",
            "discount": 2,
            "quantity": 13,
            "description": "Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый",
            "photo": None
        },
        {
            "article": "H78215",
            "name": "Туфли",
            "unit": "шт.",
            "price": 4499,
            "supplier": "Karl",
            "manufacturer": "Karl",
            "category": "Мужская обувь",
            "discount": 4,
            "quantity": 5,
            "description": "Туфли karl мужские классика MYZ21AW-450A, размер 43, цвет: черный",
            "photo": None
        },
        {
            "article": "G78315",
            "name": "Ботинки",
            "unit": "шт.",
            "price": 5900,
            "supplier": "Karl",
            "manufacturer": "Рос",
            "category": "Мужская обувь",
            "discount": 2,
            "quantity": 8,
            "description": "Мужские ботинки Рос-Обувь кожаные с натуральным мехом",
            "photo": None
        },
        {
            "article": "J38416",
            "name": "Ботинки",
            "unit": "шт.",
            "price": 3800,
            "supplier": "Обувь для вас",
            "manufacturer": "Rieker",
            "category": "Мужская обувь",
            "discount": 2,
            "quantity": 16,
            "description": "B3430/14 Полуботинки мужские Rieker",
            "photo": None
        },
    ]

    count = 0
    for product_data in products_data:
        existing = db.query(Product).filter(Product.article == product_data["article"]).first()
        if not existing:
            product = Product(**product_data)
            db.add(product)
            count += 1

    db.commit()
    print(f"Загружено товаров: {count}")


def load_orders(db: Session):
    print("Загрузка заказов...")

    orders_data = [
        {
            "order_number": "270225-1",
            "order_date": datetime(2025, 2, 27).date(),
            "delivery_date": datetime(2025, 4, 20).date(),
            "pickup_point_id": 1,
            "client_full_name": "Степанов Михаил Артёмович",
            "code": 901,
            "status": "Завершен",
            "products": ["A11214", "F6358R4"]
        },
        {
            "order_number": "280925-1",
            "order_date": datetime(2025, 9, 28).date(),
            "delivery_date": datetime(2025, 4, 21).date(),
            "pickup_point_id": 2,
            "client_full_name": "Никифорова Всесвяя Николаевна",
            "code": 902,
            "status": "Завершен",
            "products": ["H78215", "G78315"]
        },
    ]

    count = 0
    for order_data in orders_data:
        existing = db.query(Order).filter(Order.order_number == order_data["order_number"]).first()
        if not existing:
            products = order_data.pop("products")
            order = Order(**order_data)
            db.add(order)
            db.flush()

            for product_id in products:
                stmt = order_product.insert().values(
                    order_id=order.id,
                    product_id=product_id,
                    quantity=1
                )
                db.execute(stmt)

            count += 1

    db.commit()
    print(f"Загружено заказов: {count}")


def init_database():
    print("Начало инициализации базы данных...")

    create_tables()

    db = SessionLocal()
    try:
        load_pickup_points(db)
        load_users(db)
        load_products(db)
        load_orders(db)

        print("База данных успешно инициализирована!")
        print("\nТестовые учетные записи:")
        print("  Администратор: login=admin, password=admin")
        print("  Менеджер: login=manager, password=manager")
        print("  Клиент: login=client, password=client")

    except Exception as e:
        print(f"Ошибка при инициализации: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()