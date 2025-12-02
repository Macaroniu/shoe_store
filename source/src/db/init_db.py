import os
import sys

from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.db.database import SessionLocal, engine
from src.db.models.models import Base, PickupPoint, Product, User
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
        {
            "role": "авторизованный клиент",
            "full_name": "Михайлюк Анна Вячеславовна",
            "login": "client",
            "password": "client",
        },
    ]

    for user_data in users_data:
        existing = db.query(User).filter(User.login == user_data["login"]).first()
        if not existing:
            user = User(
                role=user_data["role"],
                full_name=user_data["full_name"],
                login=user_data["login"],
                password=get_password_hash(user_data["password"]),
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

    products_data = []

    count = 0
    for product_data in products_data:
        existing = db.query(Product).filter(Product.article == product_data["article"]).first()
        if not existing:
            product = Product(**product_data)
            db.add(product)
            count += 1

    db.commit()
    print(f"Загружено товаров: {count}")


def init_database():
    print("Начало инициализации базы данных...")

    create_tables()

    db = SessionLocal()
    try:
        load_pickup_points(db)
        load_users(db)
        load_products(db)

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
