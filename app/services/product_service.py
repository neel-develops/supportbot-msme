"""
Product service — lookup, fuzzy match, and CRUD helpers.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import Product

logger = logging.getLogger(__name__)


def get_product_info(db: Session, product_name: str) -> Optional[dict]:
    """
    Look up a product by name (case-insensitive, partial match).

    Returns a dict with name, price, stock, and description — or None if not found.
    """
    if not product_name:
        return None

    search_term = product_name.strip().lower()

    # Exact match first
    product = (
        db.query(Product)
        .filter(Product.name.ilike(search_term))
        .first()
    )

    # Fallback: partial match
    if not product:
        product = (
            db.query(Product)
            .filter(Product.name.ilike(f"%{search_term}%"))
            .first()
        )

    if not product:
        logger.info("Product not found for query: '%s'", product_name)
        return None

    logger.info("Product found: %s (stock=%d)", product.name, product.stock)
    return {
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "description": product.description,
    }


def get_all_products(db: Session) -> list[dict]:
    """Return all products as a list of dicts."""
    products = db.query(Product).order_by(Product.name).all()
    return [p.to_dict() for p in products]


def is_in_stock(db: Session, product_name: str) -> bool:
    """Return True if the product exists and has stock > 0."""
    info = get_product_info(db, product_name)
    return bool(info and info["stock"] > 0)
