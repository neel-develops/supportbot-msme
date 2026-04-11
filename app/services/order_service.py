"""
Order service — look up order status for customer support queries.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import Order

logger = logging.getLogger(__name__)


def get_order_by_id(db: Session, order_id: str) -> Optional[dict]:
    """Look up order by order ID (e.g. ORD-1001)."""
    order = db.query(Order).filter(Order.order_id.ilike(order_id.strip())).first()
    if not order:
        logger.info("Order not found: %s", order_id)
        return None
    return order.to_dict()


def get_orders_by_customer(db: Session, customer_number: str) -> list[dict]:
    """Return all orders for a given customer phone number."""
    orders = (
        db.query(Order)
        .filter(Order.customer_number == customer_number)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [o.to_dict() for o in orders]


def get_all_orders(db: Session) -> list[dict]:
    """Return all orders."""
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [o.to_dict() for o in orders]
