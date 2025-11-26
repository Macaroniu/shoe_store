from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Table
from sqlalchemy.orm import relationship
from src.db.database import Base

order_product = Table(
    'order_product',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id', ondelete='CASCADE')),
    Column('product_id', String, ForeignKey('products.article', ondelete='CASCADE')),
    Column('quantity', Integer, nullable=False, default=1)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)


class PickupPoint(Base):
    __tablename__ = "pickup_points"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False, unique=True)

    orders = relationship("Order", back_populates="pickup_point")


class Product(Base):
    __tablename__ = "products"

    article = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    supplier = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    category = Column(String, nullable=False)
    discount = Column(Integer, default=0)
    quantity = Column(Integer, default=0)
    description = Column(String)
    photo = Column(String)

    orders = relationship("Order", secondary=order_product, back_populates="products")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=False)
    pickup_point_id = Column(Integer, ForeignKey('pickup_points.id'))
    client_full_name = Column(String, nullable=False)
    code = Column(Integer, nullable=False)
    status = Column(String, nullable=False)

    pickup_point = relationship("PickupPoint", back_populates="orders")
    products = relationship("Product", secondary=order_product, back_populates="orders")