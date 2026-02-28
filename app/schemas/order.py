from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    product_id: int
    quantity: int = Field(ge=1, description="Quantity must be at least 1")


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    items: List[OrderItemCreate] = Field(min_length=1, description="At least one item required")


class OrderItemResponse(BaseModel):
    """Schema for order item in responses"""
    id: int
    product_id: int
    quantity: int
    unit_price: float
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for order in responses"""
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus