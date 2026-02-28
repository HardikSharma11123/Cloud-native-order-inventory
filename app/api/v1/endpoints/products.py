from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.product import BulkProductCreate, ProductCreate, ProductUpdate, ProductResponse, TopSellingProduct
from app.services import product_service
from app.core.dependencies import get_current_user, require_role
from app.models.users import User

router = APIRouter()


@router.get("/",response_model=List[ProductResponse])
def list_products(
    skip:int=Query(0,ge=0),
    limit:int=Query(1,ge=1, le=100),
    category:str=Query(None),
    db:Session=Depends(get_db)
):
    if category:
        products = product_service.get_products_by_category(db, category)
    else:
        products = product_service.get_products(db, skip=skip, limit=limit)
    
    return products

@router.get("/top-selling", response_model=List[TopSellingProduct])
def get_top_selling(
    limit: int = Query(10, ge=1, le=50, description="Number of top products to return"),
    db: Session = Depends(get_db)
):
    top_products = product_service.get_top_selling_products(db, limit=limit)
    return top_products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    return product_service.create_product(db, product)



@router.post("/bulk", response_model=List[ProductResponse], status_code=status.HTTP_201_CREATED)
def create_products_bulk(
    bulk_data: BulkProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Create multiple products at once (admin only)"""
    created_products = product_service.create_products_bulk(db, bulk_data.products)
    return created_products

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    updated_product = product_service.update_product(db, product_id, product_update)
    
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return updated_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    success = product_service.delete_product(db, product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return None 

