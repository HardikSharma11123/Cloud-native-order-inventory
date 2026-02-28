from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    name:str
    description:str
    price:float
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TopSellingProduct(BaseModel):
    """Schema for top selling product"""
    id: int
    name: str
    price: float
    category: Optional[str] = None
    total_sold: int
    total_revenue: float  # Add this

class BulkProductCreate(BaseModel):
    """Schema for creating multiple products at once"""
    products: List[ProductBase]