from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.utils import require_admin, require_manager_or_admin
from src.db.database import get_db
from src.db.models.models import Order as OrderModel
from src.db.models.models import PickupPoint
from src.db.models.models import Product as ProductModel
from src.db.models.models import User, order_product
from src.schemas.order import Order, OrderCreate, OrderUpdate
from src.schemas.order import PickupPoint as PickupPointSchema

router = APIRouter(prefix="/api/orders", tags=["orders"])


def generate_order_number(order_date: date, count: int) -> str:
    return f"{order_date.strftime('%d%m%y')}-{count}"


@router.get("/pickup-points", response_model=list[PickupPointSchema])
async def get_pickup_points(current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    points = db.query(PickupPoint).all()
    return points


@router.get("", response_model=list[Order])
async def get_orders(current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)):
    orders = db.query(OrderModel).all()

    result = []
    for order in orders:
        order_dict = Order.model_validate(order).model_dump()
        if order.pickup_point:
            order_dict["pickup_address"] = order.pickup_point.address
        result.append(order_dict)

    return result


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: int, current_user: User = Depends(require_manager_or_admin), db: Session = Depends(get_db)
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    order_dict = Order.model_validate(order).model_dump()
    if order.pickup_point:
        order_dict["pickup_address"] = order.pickup_point.address

    return order_dict


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    pickup_point = db.query(PickupPoint).filter(PickupPoint.id == order.pickup_point_id).first()
    if not pickup_point:
        raise HTTPException(status_code=404, detail="Пункт выдачи не найден")

    for product_item in order.products:
        product = db.query(ProductModel).filter(ProductModel.article == product_item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар {product_item.product_id} не найден")

    orders_count = db.query(OrderModel).filter(OrderModel.order_date == order.order_date).count()
    order_number = generate_order_number(order.order_date, orders_count + 1)

    db_order = OrderModel(
        order_number=order_number,
        order_date=order.order_date,
        delivery_date=order.delivery_date,
        pickup_point_id=order.pickup_point_id,
        client_full_name=order.client_full_name,
        code=order.code,
        status=order.status,
    )

    db.add(db_order)
    db.flush()

    for product_item in order.products:
        stmt = order_product.insert().values(
            order_id=db_order.id, product_id=product_item.product_id, quantity=product_item.quantity
        )
        db.execute(stmt)

    db.commit()
    db.refresh(db_order)

    order_dict = Order.model_validate(db_order).model_dump()
    order_dict["pickup_address"] = pickup_point.address

    return order_dict


@router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: int, order_update: OrderUpdate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    update_data = order_update.model_dump(exclude_unset=True, exclude={"products"})

    for field, value in update_data.items():
        setattr(db_order, field, value)

    if order_update.products is not None:
        db.execute(order_product.delete().where(order_product.c.order_id == order_id))

        for product_item in order_update.products:
            product = db.query(ProductModel).filter(ProductModel.article == product_item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Товар {product_item.product_id} не найден")

            stmt = order_product.insert().values(
                order_id=order_id, product_id=product_item.product_id, quantity=product_item.quantity
            )
            db.execute(stmt)

    db.commit()
    db.refresh(db_order)

    order_dict = Order.model_validate(db_order).model_dump()
    if db_order.pickup_point:
        order_dict["pickup_address"] = db_order.pickup_point.address

    return order_dict


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    db.execute(order_product.delete().where(order_product.c.order_id == order_id))

    db.delete(order)
    db.commit()

    return None
