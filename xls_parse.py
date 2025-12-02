"""
Скрипт для импорта данных из Excel файлов в базу данных
Импортирует пользователей, пункты выдачи и заказы
Версия 4.0 - для структуры с static/xls/
"""
import sys
import os
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

# Добавляем путь к source в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(current_dir, 'source')
if os.path.exists(source_dir):
    sys.path.insert(0, source_dir)

# Импорты для работы с БД и моделями
try:
    from src.db.database import SessionLocal, engine
    from src.db.models.models import Base, User, PickupPoint, Order, Product, order_product
    from src.utils.security import get_password_hash
except ImportError as e:
    print("❌ Ошибка импорта модулей!")
    print(f"   Детали: {e}")
    print(f"   Текущая директория: {os.getcwd()}")
    print("\n💡 Решение:")
    print("   Убедитесь что скрипт запущен из корня проекта")
    sys.exit(1)


def import_users_from_excel(db: Session, filepath: str):
    """Импортирует пользователей из Excel файла"""
    print(f"\nИмпорт пользователей из файла: {filepath}")

    try:
        df = pd.read_excel(filepath)

        required_columns = ['Роль сотрудника', 'ФИО', 'Логин', 'Пароль']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Отсутствует колонка: {col}")

        imported_count = 0
        skipped_count = 0

        for _, row in df.iterrows():
            login = str(row['Логин']).strip()

            existing_user = db.query(User).filter(User.login == login).first()

            if existing_user:
                print(f"  ⚠️  Пользователь с логином '{login}' уже существует, пропускаем...")
                skipped_count += 1
                continue

            user = User(
                role=str(row['Роль сотрудника']).strip(),
                full_name=str(row['ФИО']).strip(),
                login=login,
                password=get_password_hash(str(row['Пароль']).strip())
            )

            db.add(user)
            imported_count += 1
            print(f"  ✅ Добавлен: {user.full_name} ({user.login}) - {user.role}")

        db.commit()

        print(f"\n📊 Итого импортировано пользователей: {imported_count}")
        print(f"📊 Пропущено (уже существуют): {skipped_count}")

        return imported_count

    except Exception as e:
        print(f"❌ Ошибка при импорте пользователей: {e}")
        db.rollback()
        raise


def import_pickup_points_from_excel(db: Session, filepath: str):
    """Импортирует пункты выдачи из Excel файла"""
    print(f"\nИмпорт пунктов выдачи из файла: {filepath}")

    try:
        df = pd.read_excel(filepath)

        addresses = []

        # Первый адрес - это название колонки
        if len(df.columns) > 0:
            addresses.append(str(df.columns[0]).strip())

        # Остальные адреса - в первой колонке
        for _, row in df.iterrows():
            address = str(row.iloc[0]).strip()
            if address and address != 'nan':
                addresses.append(address)

        imported_count = 0
        skipped_count = 0

        for address in addresses:
            existing_point = db.query(PickupPoint).filter(
                PickupPoint.address == address
            ).first()

            if existing_point:
                print(f"  ⚠️  Пункт выдачи '{address}' уже существует, пропускаем...")
                skipped_count += 1
                continue

            point = PickupPoint(address=address)
            db.add(point)
            imported_count += 1
            print(f"  ✅ Добавлен: {address}")

        db.commit()

        print(f"\n📊 Итого импортировано пунктов выдачи: {imported_count}")
        print(f"📊 Пропущено (уже существуют): {skipped_count}")

        return imported_count

    except Exception as e:
        print(f"❌ Ошибка при импорте пунктов выдачи: {e}")
        db.rollback()
        raise


def parse_order_products(products_str: str):
    """
    Парсит строку с артикулами и количествами
    Формат: "А112Т4, 2, F635R4, 2"
    """
    products = []
    parts = [p.strip() for p in products_str.split(',')]

    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            article = parts[i].strip()
            try:
                quantity = int(parts[i + 1].strip())
                products.append({
                    'product_id': article,
                    'quantity': quantity
                })
            except ValueError:
                print(f"  ⚠️  Не удалось распарсить количество для артикула {article}")

    return products


def import_orders_from_excel(db: Session, filepath: str):
    """Импортирует заказы из Excel файла"""
    print(f"\nИмпорт заказов из файла: {filepath}")

    try:
        df = pd.read_excel(filepath)

        required_columns = [
            'Номер заказа',
            'Артикул заказа',
            'Дата заказа',
            'Дата доставки',
            'Адрес пункта выдачи',
            'ФИО авторизированного клиента',
            'Код для получения',
            'Статус заказа'
        ]

        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Отсутствует колонка: {col}")

        imported_count = 0
        skipped_count = 0
        errors_count = 0

        for idx, row in df.iterrows():
            try:
                order_number = str(row['Номер заказа']).strip()

                order_date = pd.to_datetime(row['Дата заказа'])
                delivery_date = pd.to_datetime(row['Дата доставки'])

                # Генерируем номер в формате DDMMYY-N
                order_num = f"{order_date.strftime('%d%m%y')}-{order_number}"

                existing_order = db.query(Order).filter(
                    Order.order_number == order_num
                ).first()

                if existing_order:
                    print(f"  ⚠️  Заказ '{order_num}' уже существует, пропускаем...")
                    skipped_count += 1
                    continue

                # Находим пункт выдачи
                address = str(row['Адрес пункта выдачи']).strip()
                pickup_point = db.query(PickupPoint).filter(
                    PickupPoint.address == address
                ).first()

                if not pickup_point:
                    print(f"  ⚠️  Пункт выдачи '{address}' не найден для заказа {order_num}")
                    errors_count += 1
                    continue

                # Парсим товары
                products_str = str(row['Артикул заказа']).strip()
                products = parse_order_products(products_str)

                if not products:
                    print(f"  ⚠️  Не удалось распарсить товары для заказа {order_num}")
                    errors_count += 1
                    continue

                # Создаем заказ
                order = Order(
                    order_number=order_num,
                    order_date=order_date.date(),
                    delivery_date=delivery_date.date(),
                    pickup_point_id=pickup_point.id,
                    client_full_name=str(row['ФИО авторизированного клиента']).strip(),
                    code=int(row['Код для получения']),
                    status=str(row['Статус заказа']).strip()
                )

                db.add(order)
                db.flush()  # Получаем ID заказа

                # Добавляем товары
                products_added = 0
                for product_info in products:
                    product_id = product_info['product_id']
                    quantity = product_info['quantity']

                    product = db.query(Product).filter(
                        Product.article == product_id
                    ).first()

                    if not product:
                        print(f"  ⚠️  Товар с артикулом '{product_id}' не найден, пропускаем...")
                        continue

                    stmt = order_product.insert().values(
                        order_id=order.id,
                        product_id=product_id,
                        quantity=quantity
                    )
                    db.execute(stmt)
                    products_added += 1

                if products_added == 0:
                    print(f"  ⚠️  В заказ {order_num} не добавлено ни одного товара (товары не найдены)")
                    db.rollback()
                    errors_count += 1
                    continue

                imported_count += 1
                print(f"  ✅ Добавлен заказ: {order_num} ({products_added} товаров)")

            except Exception as e:
                print(f"  ❌ Ошибка при обработке заказа {idx + 1}: {e}")
                errors_count += 1
                continue

        db.commit()

        print(f"\n📊 Итого импортировано заказов: {imported_count}")
        print(f"📊 Пропущено (уже существуют): {skipped_count}")
        print(f"📊 Ошибок: {errors_count}")

        return imported_count

    except Exception as e:
        print(f"❌ Ошибка при импорте заказов: {e}")
        db.rollback()
        raise


def main():
    """Главная функция для запуска импорта"""
    print("=" * 70)
    print("ИМПОРТ ДАННЫХ ИЗ EXCEL ФАЙЛОВ")
    print("=" * 70)
    print(f"Текущая директория: {os.getcwd()}\n")

    # Пути к файлам в static/xls/
    users_file = "/Users/egor/PycharmProjects/shoe_storerererere/static/xls/user_import.xlsx"
    pickup_points_file = "/Users/egor/PycharmProjects/shoe_storerererere/static/xls/Пункты выдачи_import.xlsx"  # ВАЖНО: пробел, не подчеркивание!
    orders_file = "/Users/egor/PycharmProjects/shoe_storerererere/static/xls/Заказ_import.xlsx"

    # Проверка наличия файлов
    if not os.path.exists(users_file):
        print(f"❌ Файл {users_file} не найден!")
        print(f"   Поместите файл в: {os.getcwd()}/static/xls/")
        return

    if not os.path.exists(pickup_points_file):
        print(f"❌ Файл {pickup_points_file} не найден!")
        print(f"   Поместите файл в: {os.getcwd()}/static/xls/")
        return

    if not os.path.exists(orders_file):
        print(f"⚠️  Файл {orders_file} не найден!")
        print(f"   Пропускаем импорт заказов...")
        orders_file = None

    # Создаем сессию БД
    db = SessionLocal()

    try:
        # Импортируем в правильном порядке
        points_imported = import_pickup_points_from_excel(db, pickup_points_file)
        users_imported = import_users_from_excel(db, users_file)

        orders_imported = 0
        if orders_file:
            orders_imported = import_orders_from_excel(db, orders_file)

        print("\n" + "=" * 70)
        print("✨ ИМПОРТ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 70)
        print(f"Всего импортировано:")
        print(f"  👥 Пользователей: {users_imported}")
        print(f"  📍 Пунктов выдачи: {points_imported}")
        if orders_file:
            print(f"  📦 Заказов: {orders_imported}")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()