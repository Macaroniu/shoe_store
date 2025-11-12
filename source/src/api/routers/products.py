from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.db.database import get_db
from src.db.models import Product as ProductModel, User
from src.schemas.product import Product, ProductCreate, ProductUpdate, ProductWithFinalPrice
from src.api.dependencies import get_current_user, require_admin
from src.utils.image_handler import save_product_image, delete_product_image, get_image_path

router = APIRouter(prefix="/api/products", tags=["products"])


def calculate_final_price(product: ProductModel) -> dict:
    final_price = product.price
    if product.discount > 0:
        final_price = product.price * (1 - product.discount / 100)

    return {
        **Product.model_validate(product).model_dump(),
        "final_price": round(final_price, 2),
        "out_of_stock": product.quantity == 0,
        "photo": get_image_path(product.photo)
    }


@router.get("", response_model=list[ProductWithFinalPrice])
async def get_products(
        search: str | None = None,
        supplier: str | None = None,
        sort_by_quantity: str | None = None,  # 'asc' или 'desc'
        current_user: User | None = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    query = db.query(ProductModel)

    can_filter = current_user and current_user.role in ["Менеджер", "Администратор"]

    if can_filter:
        if search:
            search_filter = or_(
                ProductModel.article.ilike(f"%{search}%"),
                ProductModel.name.ilike(f"%{search}%"),
                ProductModel.supplier.ilike(f"%{search}%"),
                ProductModel.manufacturer.ilike(f"%{search}%"),
                ProductModel.category.ilike(f"%{search}%"),
                ProductModel.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        if supplier and supplier != "Все поставщики":
            query = query.filter(ProductModel.supplier == supplier)

        if sort_by_quantity == "asc":
            query = query.order_by(ProductModel.quantity.asc())
        elif sort_by_quantity == "desc":
            query = query.order_by(ProductModel.quantity.desc())

    products = query.all()
    return [calculate_final_price(p) for p in products]


@router.get("/suppliers")
async def get_suppliers(
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    suppliers = db.query(ProductModel.supplier).distinct().all()
    return ["Все поставщики"] + [s[0] for s in suppliers]


@router.get("/{article}", response_model=ProductWithFinalPrice)
async def get_product(
        article: str,
        current_user: User | None = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.article == article).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    return calculate_final_price(product)


@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    existing = db.query(ProductModel).filter(ProductModel.article == product.article).first()
    if existing:
        raise HTTPException(status_code=400, detail="Товар с таким артикулом уже существует")

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.put("/{article}", response_model=Product)
async def update_product(
        article: str,
        product_update: ProductUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    db_product = db.query(ProductModel).filter(ProductModel.article == article).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)

    return db_product


@router.post("/{article}/upload-image")
async def upload_product_image(
        article: str,
        file: UploadFile = File(...),
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    product = db.query(ProductModel).filter(ProductModel.article == article).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    if product.photo:
        delete_product_image(product.photo)

    filename = await save_product_image(file, article)
    product.photo = filename

    db.commit()

    return {"filename": filename, "path": get_image_path(filename)}


@router.delete("/{article}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
        article: str,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    from src.db.models import order_product

    product = db.query(ProductModel).filter(ProductModel.article == article).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    has_orders = db.query(order_product).filter(order_product.c.product_id == article).first()
    if has_orders:
        raise HTTPException(
            status_code=400,
            detail="Невозможно удалить товар, который присутствует в заказах"
        )

    if product.photo:
        delete_product_image(product.photo)

    db.delete(product)
    db.commit()

    return None