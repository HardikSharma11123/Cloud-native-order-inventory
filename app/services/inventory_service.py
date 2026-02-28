from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.inventory import Inventory
from app.models.product import Product
from app.schemas.inventory import InventoryCreate, InventoryUpdate


def get_all_inventory(db: Session) -> List[Inventory]:
    return db.query(Inventory).all()

def get_inventory_by_product_id(db: Session, product_id: int) -> Optional[Inventory]:
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()


def create_inventory(db: Session, inventory: InventoryCreate) -> Optional[Inventory]:
    product = db.query(Product).filter(Product.id == inventory.product_id).first()
    if not product:
        return None
    
    existing = get_inventory_by_product_id(db, inventory.product_id)
    if existing:
        return None  
    
    db_inventory = Inventory(
        product_id=inventory.product_id,
        quantity=inventory.quantity,
        reserved_quantity=0
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_inventory(db: Session, product_id: int, inventory_update: InventoryUpdate) -> Optional[Inventory]:
    db_inventory = get_inventory_by_product_id(db, product_id)
    
    if not db_inventory:
        return None
    
    update_data = inventory_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_inventory, field, value)
    
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def get_available_quantity(db: Session, product_id: int) -> Optional[int]:
    inventory = get_inventory_by_product_id(db, product_id)
    
    if not inventory:
        return None
    
    return inventory.quantity - inventory.reserved_quantity

def create_inventories_bulk(db: Session, inventories: List[InventoryCreate]) -> List[Inventory]:
    """Create multiple inventory records at once"""
    from app.models.product import Product
    
    db_inventories = []
    
    for inventory in inventories:
        # Check if product exists
        product = db.query(Product).filter(Product.id == inventory.product_id).first()
        if not product:
            continue  # Skip non-existent products
        
        # Check if inventory already exists
        existing = get_inventory_by_product_id(db, inventory.product_id)
        if existing:
            continue  # Skip if already exists
        
        db_inventory = Inventory(
            product_id=inventory.product_id,
            quantity=inventory.quantity,
            reserved_quantity=0
        )
        db_inventories.append(db_inventory)
    
    if db_inventories:
        db.add_all(db_inventories)
        db.commit()
        for db_inv in db_inventories:
            db.refresh(db_inv)
    
    return db_inventories