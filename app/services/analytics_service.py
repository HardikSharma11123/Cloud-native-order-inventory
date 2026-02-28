from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from datetime import datetime, timedelta
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product


def get_top_selling_products(db: Session, limit: int = 10) -> List[Dict]:
    """Get top N selling products with revenue"""
    results = (
        db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue')
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status != OrderStatus.CANCELLED)
        .group_by(Product.id)
        .order_by(desc('total_sold'))
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": row.id,
            "name": row.name,
            "total_sold": int(row.total_sold),
            "total_revenue": float(row.total_revenue)
        }
        for row in results
    ]


def get_revenue_over_time(db: Session, days: int = 30) -> List[Dict]:
    """Get daily revenue for the last N days"""
    start_date = datetime.now() - timedelta(days=days)
    
    results = (
        db.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        )
        .filter(
            Order.created_at >= start_date,
            Order.status != OrderStatus.CANCELLED
        )
        .group_by(func.date(Order.created_at))
        .order_by('date')
        .all()
    )
    
    return [
        {
            "date": row.date.strftime('%Y-%m-%d'),
            "revenue": float(row.revenue)
        }
        for row in results
    ]


def get_revenue_by_product(db: Session) -> List[Dict]:
    """Get revenue breakdown by product"""
    results = (
        db.query(
            Product.id,
            Product.name,
            Product.category,
            func.sum(OrderItem.quantity).label('units_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status != OrderStatus.CANCELLED)
        .group_by(Product.id)
        .order_by(desc('revenue'))
        .all()
    )
    
    return [
        {
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "units_sold": int(row.units_sold),
            "revenue": float(row.revenue)
        }
        for row in results
    ]


def get_dashboard_stats(db: Session) -> Dict:
    """Get overall dashboard statistics"""
    # Total revenue
    total_revenue = db.query(
        func.sum(Order.total_amount)
    ).filter(Order.status != OrderStatus.CANCELLED).scalar() or 0
    
    # Total orders
    total_orders = db.query(Order).filter(Order.status != OrderStatus.CANCELLED).count()
    
    # Total products sold
    total_products_sold = db.query(
        func.sum(OrderItem.quantity)
    ).join(Order).filter(Order.status != OrderStatus.CANCELLED).scalar() or 0
    
    # Pending orders
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    
    return {
        "total_revenue": float(total_revenue),
        "total_orders": total_orders,
        "total_products_sold": int(total_products_sold),
        "pending_orders": pending_orders
    }