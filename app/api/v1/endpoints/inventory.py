from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.order import OrderItem
from app.models.product import Product
from app.schemas.inventory import BulkInventoryCreate, InventoryCreate, InventoryUpdate, InventoryResponse, InventoryWithProduct
from app.services import inventory_service
from app.core.dependencies import get_current_user, require_role
from app.models.users import User

router = APIRouter()


@router.get("/", response_model=List[InventoryResponse])
def list_inventory(db: Session = Depends(get_db)):
    return inventory_service.get_all_inventory(db)



@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    inventory = inventory_service.get_inventory_by_product_id(db, product_id)
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found for this product"
        )
    
    return inventory


@router.get("/{product_id}/available", response_model=dict)
def get_available_stock(product_id: int, db: Session = Depends(get_db)):
    available = inventory_service.get_available_quantity(db, product_id)
    
    if available is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found for this product"
        )
    
    return {
        "product_id": product_id,
        "available_quantity": available
    }


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "warehouse_manager"]))
):
    db_inventory = inventory_service.create_inventory(db, inventory)
    
    if not db_inventory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found or inventory already exists"
        )
    
    return db_inventory

@router.post("/bulk", response_model=List[InventoryResponse], status_code=status.HTTP_201_CREATED)
def create_inventories_bulk(
    bulk_data: BulkInventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "warehouse_manager"]))
):
    """Create inventory for multiple products at once"""
    created_inventories = inventory_service.create_inventories_bulk(db, bulk_data.inventories)
    return created_inventories

@router.put("/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: int,
    inventory_update: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "warehouse_manager"]))
):
    updated_inventory = inventory_service.update_inventory(db, product_id, inventory_update)
    
    if not updated_inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found"
        )
    
    return updated_inventory

