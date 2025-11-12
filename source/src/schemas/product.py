from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    article: str
    name: str
    unit: str
    price: float = Field(gt=0)
    supplier: str
    manufacturer: str
    category: str
    discount: int = Field(ge=0, le=100, default=0)
    quantity: int = Field(ge=0, default=0)
    description: str | None = None
    photo: str | None = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    price: float | None = Field(None, gt=0)
    supplier: str | None = None
    manufacturer: str | None = None
    category: str | None = None
    discount: int | None = Field(None, ge=0, le=100)
    quantity: int | None = Field(None, ge=0)
    description: str | None = None
    photo: str | None = None

class Product(ProductBase):
    class Config:
        from_attributes = True

class ProductWithFinalPrice(Product):
    final_price: float
    out_of_stock: bool