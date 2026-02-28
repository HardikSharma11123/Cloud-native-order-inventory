from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.schemas.product import ProductResponse


class InventoryCreate(BaseModel):
    """Schema for creating inventory record"""
    product_id: int
    quantity: int = Field(default=0, ge=0, description="Total quantity must be >= 0")


class InventoryUpdate(BaseModel):
    """Schema for updating inventory"""
    quantity: Optional[int] = Field(default=None, ge=0)
    reserved_quantity: Optional[int] = Field(default=None, ge=0)


class InventoryResponse(BaseModel):
    """Schema for inventory in responses"""
    id: int
    product_id: int
    quantity: int
    reserved_quantity: int
    last_updated: datetime
    
    class Config:
        from_attributes = True
from typing import List

class BulkInventoryCreate(BaseModel):
    """Schema for creating multiple inventory records"""
    inventories: List[InventoryCreate]

class InventoryWithProduct(InventoryResponse):
    """Inventory with product details included"""
    product: "ProductResponse"  # Forward reference as string
    
    class Config:
        from_attributes = True