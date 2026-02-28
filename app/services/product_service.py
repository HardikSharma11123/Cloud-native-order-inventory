from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.order import OrderItem
from sqlalchemy import func, desc

def get_products(db:Session, skip: int=0,limit:int=100)->List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()

def get_product_by_id(db:Session,product_id:int)->Optional[Product]:
    return db.query(Product).filter(Product.id==product_id).first()

def get_products_by_category(db: Session, category: str) -> List[Product]:
    return db.query(Product).filter(Product.category==category).all()

def create_product(db: Session, product: ProductCreate) -> Product:
    db_product=Product(
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    db_product = get_product_by_id(db, product_id)
    
    if not db_product:
        return None
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """Delete a product"""
    db_product = get_product_by_id(db, product_id)
    
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True



def get_top_selling_products(db: Session, limit: int = 10) -> List[dict]:
    results = (
        db.query(
            Product.id,
            Product.name,
            Product.price,
            Product.category,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue')
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .group_by(Product.id)
        .order_by(desc('total_sold'))
        .limit(limit)
        .all()
    )
    
    # Convert to list of dicts
    top_products = []
    for row in results:
        top_products.append({
            "id": row.id,
            "name": row.name,
            "price": row.price,
            "category": row.category,
            "total_sold": row.total_sold,
            "total_revenue": float(row.total_revenue) if row.total_revenue else 0.0
        })
    
    return top_products
    

def create_products_bulk(db: Session, products: List[ProductCreate]) -> List[Product]:
    """Create multiple products at once"""
    db_products = []
    
    for product in products:
        db_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category
        )
        db_products.append(db_product)
    
    # Add all products in one transaction
    db.add_all(db_products)
    db.commit()
    
    # Refresh all to get IDs
    for db_product in db_products:
        db.refresh(db_product)
    
    return db_products