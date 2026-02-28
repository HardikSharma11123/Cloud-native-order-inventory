from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.session import get_db
from app.services import analytics_service
from app.core.dependencies import require_role
from app.models.users import User

router = APIRouter()


@router.get("/dashboard-stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
) -> Dict:
    """Get overall dashboard statistics (admin only)"""
    return analytics_service.get_dashboard_stats(db)


@router.get("/top-selling")
def get_top_selling(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
) -> List[Dict]:
    """Get top selling products with revenue (admin only)"""
    return analytics_service.get_top_selling_products(db, limit)


@router.get("/revenue-over-time")
def get_revenue_over_time(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
) -> List[Dict]:
    """Get daily revenue for last N days (admin only)"""
    return analytics_service.get_revenue_over_time(db, days)


@router.get("/revenue-by-product")
def get_revenue_by_product(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
) -> List[Dict]:
    """Get revenue breakdown by product (admin only)"""
    return analytics_service.get_revenue_by_product(db)