"""
Database engine, session factory, and seed data for SupportBot MSME.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./supportbot.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables and seed sample data if the products table is empty."""
    from app.database.models import Base, Product, Order  # noqa: F401 — import triggers table registration

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    db: Session = SessionLocal()
    try:
        _seed_products(db)
        _seed_orders(db)
    finally:
        db.close()


def _seed_products(db: Session) -> None:
    from app.database.models import Product

    if db.query(Product).count() > 0:
        return  # Already seeded

    sample_products = [
        Product(
            name="Laptop Bag",
            price=999.0,
            stock=5,
            description="Waterproof padded bag for laptops up to 15.6 inches.",
        ),
        Product(
            name="Wireless Mouse",
            price=499.0,
            stock=20,
            description="Ergonomic wireless mouse with 12-month battery life.",
        ),
        Product(
            name="Mechanical Keyboard",
            price=1999.0,
            stock=8,
            description="TKL mechanical keyboard with blue switches and RGB backlight.",
        ),
        Product(
            name="USB-C Hub",
            price=1299.0,
            stock=15,
            description="7-in-1 USB-C hub with HDMI, USB 3.0, SD card, and PD charging.",
        ),
        Product(
            name="Monitor Stand",
            price=799.0,
            stock=12,
            description="Adjustable aluminium monitor riser with cable management.",
        ),
    ]

    db.add_all(sample_products)
    db.commit()
    logger.info("Seeded %d sample products.", len(sample_products))


def _seed_orders(db: Session) -> None:
    from app.database.models import Order

    if db.query(Order).count() > 0:
        return

    sample_orders = [
        Order(
            order_id="ORD-1001",
            customer_name="Rahul Sharma",
            customer_number="919876543210",
            product_name="Laptop Bag",
            status="Out for delivery",
            delivery_date="13 April 2026",
        ),
        Order(
            order_id="ORD-1002",
            customer_name="Priya Mehta",
            customer_number="919812345678",
            product_name="Wireless Mouse",
            status="Delivered",
            delivery_date="10 April 2026",
        ),
        Order(
            order_id="ORD-1003",
            customer_name="Arjun Patel",
            customer_number="919898765432",
            product_name="Mechanical Keyboard",
            status="Processing",
            delivery_date="15 April 2026",
        ),
    ]

    db.add_all(sample_orders)
    db.commit()
    logger.info("Seeded %d sample orders.", len(sample_orders))
