"""
Database models for SupportBot MSME.
Defines Products, Orders, and Messages tables.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return f"<Product(name={self.name}, price={self.price}, stock={self.stock})>"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), nullable=False, unique=True, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_number = Column(String(20), nullable=False)
    product_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    delivery_date = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "customer_number": self.customer_number,
            "product_name": self.product_name,
            "status": self.status,
            "delivery_date": self.delivery_date,
            "created_at": str(self.created_at),
        }

    def __repr__(self) -> str:
        return f"<Order(order_id={self.order_id}, status={self.status})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    customer_number = Column(String(20), nullable=False, index=True)
    message_text = Column(Text, nullable=False)
    detected_intent = Column(String(50), nullable=True)
    bot_reply = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_number": self.customer_number,
            "message_text": self.message_text,
            "detected_intent": self.detected_intent,
            "bot_reply": self.bot_reply,
            "timestamp": str(self.timestamp),
        }

    def __repr__(self) -> str:
        return f"<Message(from={self.customer_number}, intent={self.detected_intent})>"
