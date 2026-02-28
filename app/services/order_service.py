from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.users import User
from app.schemas.order import OrderCreate, OrderItemCreate
from app.cache.locks import InventoryLock


class InsufficientStockError(Exception):
    """Raised when there's not enough stock to fulfill order"""
    pass


class ProductNotFoundError(Exception):
    """Raised when a product doesn't exist"""
    pass


def get_user_orders(db: Session, user_id: int) -> List[Order]:
    """Get all orders for a user"""
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    """Get a specific order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders (admin only)"""
    return db.query(Order).offset(skip).limit(limit).all()


def create_order(db: Session, order_data: OrderCreate, user_id: int) -> Order:
    """
    Create an order with Redis locking to prevent race conditions.
    
    This is the critical function that uses distributed locking.
    """
    
    # Step 1: Validate all products exist and collect product info
    product_info = {}
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ProductNotFoundError(f"Product {item.product_id} not found")
        product_info[item.product_id] = product
    
    # Step 2: Acquire locks for all products (prevents concurrent modifications)
    locks = {}
    try:
        for item in order_data.items:
            lock = InventoryLock(item.product_id, timeout=10)
            if not lock.acquire(retry_times=3, retry_delay=0.1):
                raise Exception(f"Could not acquire lock for product {item.product_id}. Please try again.")
            locks[item.product_id] = lock
        
        # Step 3: Check inventory availability and reserve stock
        for item in order_data.items:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == item.product_id
            ).first()
            
            if not inventory:
                raise InsufficientStockError(f"No inventory record for product {item.product_id}")
            
            # Calculate available quantity
            available = inventory.quantity - inventory.reserved_quantity
            
            if available < item.quantity:
                raise InsufficientStockError(
                    f"Insufficient stock for product {item.product_id}. "
                    f"Available: {available}, Requested: {item.quantity}"
                )
            
            # Reserve the inventory
            inventory.reserved_quantity += item.quantity
        
        # Step 4: Calculate total amount
        total_amount = sum(
            product_info[item.product_id].price * item.quantity
            for item in order_data.items
        )
        
        # Step 5: Create order record
        db_order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount
        )
        db.add(db_order)
        db.flush()  # Get order ID without committing yet
        
        # Step 6: Create order items
        for item in order_data.items:
            product = product_info[item.product_id]
            db_order_item = OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price  # Capture price at time of order
            )
            db.add(db_order_item)
        
        # Step 7: Commit transaction
        db.commit()
        db.refresh(db_order)
        
        return db_order
    
    finally:
        # Step 8: Always release locks (even if error occurred)
        for lock in locks.values():
            lock.release()


def confirm_order_payment(db: Session, order_id: int) -> Optional[Order]:
    """
    Confirm order payment and deduct from actual inventory.
    This moves reserved_quantity to actually deducted quantity.
    """
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    
    if order.status != OrderStatus.PENDING:
        return order  # Already processed
    
    # Deduct inventory for each item
    for item in order.items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id
        ).first()
        
        if inventory:
            # Move from reserved to actually deducted
            inventory.reserved_quantity -= item.quantity
            inventory.quantity -= item.quantity
    
    # Update order status
    order.status = OrderStatus.PROCESSING
    db.commit()
    db.refresh(order)
    
    return order


def cancel_order(db: Session, order_id: int) -> Optional[Order]:
    """
    Cancel an order and release reserved inventory.
    """
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    
    if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
        raise Exception("Cannot cancel order that has been shipped or delivered")
    
    # Release reserved inventory
    for item in order.items:
        inventory = db.query(Inventory).filter(
            Inventory.product_id == item.product_id
        ).first()
        
        if inventory and order.status == OrderStatus.PENDING:
            # Only release if still pending (not yet deducted)
            inventory.reserved_quantity -= item.quantity
    
    # Update order status
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    
    return order


def update_order_status(db: Session, order_id: int, new_status: OrderStatus) -> Optional[Order]:
    """Update order status (for warehouse/admin)"""
    order = get_order_by_id(db, order_id)
    if not order:
        return None
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    return order