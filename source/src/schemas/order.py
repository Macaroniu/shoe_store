from pydantic import BaseModel
from datetime import date

class OrderProductBase(BaseModel):
    product_id: str
    quantity: int

class OrderBase(BaseModel):
    order_number: str
    order_date: date
    delivery_date: date
    pickup_point_id: int
    client_full_name: str
    code: int
    status: str

class OrderCreate(BaseModel):
    order_date: date
    delivery_date: date
    pickup_point_id: int
    client_full_name: str
    code: int
    status: str
    products: list[OrderProductBase]

class OrderUpdate(BaseModel):
    order_date: date | None = None
    delivery_date: date | None = None
    pickup_point_id: int | None = None
    client_full_name: str | None = None
    code: int | None = None
    status: str | None = None
    products: list[OrderProductBase] | None = None

class Order(OrderBase):
    id: int
    pickup_address: str | None = None

    class Config:
        from_attributes = True

class PickupPointBase(BaseModel):
    address: str

class PickupPoint(PickupPointBase):
    id: int

    class Config:
        from_attributes = True