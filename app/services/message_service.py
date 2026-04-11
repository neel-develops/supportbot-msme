"""
Message service — save and retrieve conversation logs.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.database.models import Message

logger = logging.getLogger(__name__)


def save_message(
    db: Session,
    customer_number: str,
    message_text: str,
    bot_reply: str,
    detected_intent: Optional[str] = None,
) -> Message:
    """Persist an inbound message and bot reply to the messages table."""
    msg = Message(
        customer_number=customer_number,
        message_text=message_text,
        detected_intent=detected_intent,
        bot_reply=bot_reply,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    logger.info(
        "Message logged — from=%s intent=%s id=%d",
        customer_number,
        detected_intent,
        msg.id,
    )
    return msg


def get_recent_messages(db: Session, limit: int = 100) -> list[dict]:
    """Return the most recent messages ordered by newest first."""
    messages = (
        db.query(Message)
        .order_by(Message.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [m.to_dict() for m in messages]


def get_messages_by_customer(db: Session, customer_number: str) -> list[dict]:
    """Return full conversation history for one customer."""
    messages = (
        db.query(Message)
        .filter(Message.customer_number == customer_number)
        .order_by(Message.timestamp.asc())
        .all()
    )
    return [m.to_dict() for m in messages]


def get_message_count(db: Session) -> int:
    return db.query(Message).count()
