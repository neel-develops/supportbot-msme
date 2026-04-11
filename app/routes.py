"""
API routes for SupportBot MSME.

Endpoints:
  GET  /webhook          — WhatsApp webhook verification
  POST /webhook          — Receive inbound WhatsApp messages
  POST /simulate         — Simulate a message without WhatsApp (for testing)
  GET  /messages         — List recent messages
  GET  /products         — List all products
  GET  /health           — Health check
"""

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.intent_agent import detect_intent
from app.agents.response_agent import generate_response
from app.database.db import get_db
from app.services.message_service import get_recent_messages, get_message_count, save_message
from app.services.order_service import get_order_by_id, get_orders_by_customer
from app.services.product_service import get_all_products, get_product_info

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class SimulateRequest(BaseModel):
    customer_number: str = "919999999999"
    message: str


class WebhookResponse(BaseModel):
    status: str
    intent: str
    reply: str


# ─── Core message processing pipeline ────────────────────────────────────────

def process_message(customer_number: str, message_text: str, db: Session) -> dict:
    """
    Full pipeline:
      1. Detect intent
      2. Look up product or order data
      3. Generate reply
      4. Log conversation
      5. Return result
    """
    logger.info("Processing message from %s: '%s'", customer_number, message_text[:80])

    # Step 1 — Intent detection
    intent_result = detect_intent(message_text)
    intent = intent_result["intent"]
    product_name = intent_result.get("product_name")
    order_id = intent_result.get("order_id")

    logger.info("Detected intent: %s | product: %s | order: %s", intent, product_name, order_id)

    # Step 2 — Data lookup
    context: dict[str, Any] = {
        "product_name": product_name,
        "order_id": order_id,
    }

    if intent in ("product_inquiry", "price_inquiry") and product_name:
        product = get_product_info(db, product_name)
        context["product"] = product

    elif intent == "order_status":
        if order_id:
            order = get_order_by_id(db, order_id)
        else:
            # Try to find by customer number
            orders = get_orders_by_customer(db, customer_number)
            order = orders[0] if orders else None
        context["order"] = order

    # Step 3 — Generate reply
    reply = generate_response(intent, context, message_text)

    # Step 4 — Log
    save_message(
        db=db,
        customer_number=customer_number,
        message_text=message_text,
        bot_reply=reply,
        detected_intent=intent,
    )

    return {
        "intent": intent,
        "reply": reply,
        "context": context,
    }


# ─── WhatsApp Webhook (GET) — verification ────────────────────────────────────

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """WhatsApp Cloud API webhook verification handshake."""
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "supportbot_verify_token")

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("Webhook verified successfully.")
        return PlainTextResponse(content=hub_challenge)

    logger.warning("Webhook verification failed — token mismatch.")
    raise HTTPException(status_code=403, detail="Verification failed.")


# ─── WhatsApp Webhook (POST) — inbound messages ───────────────────────────────

@router.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive and process inbound WhatsApp messages from Meta webhook.
    Always returns 200 OK to acknowledge receipt (Meta requires this).
    """
    try:
        body = await request.json()
        logger.debug("Webhook payload: %s", body)

        # Navigate Meta's nested payload structure
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "ok", "detail": "no messages"}

        msg = messages[0]
        customer_number = msg.get("from", "unknown")
        message_text = msg.get("text", {}).get("body", "")

        if not message_text:
            return {"status": "ok", "detail": "non-text message ignored"}

        result = process_message(customer_number, message_text, db)

        # In production: call WhatsApp send API here
        # send_whatsapp_message(customer_number, result["reply"])

        return {"status": "ok", "intent": result["intent"]}

    except Exception as exc:
        logger.error("Webhook processing error: %s", exc, exc_info=True)
        return {"status": "ok", "error": "internal error — logged"}


# ─── Simulate endpoint — for local testing without WhatsApp ──────────────────

@router.post("/simulate", response_model=WebhookResponse)
async def simulate_message(payload: SimulateRequest, db: Session = Depends(get_db)):
    """
    Send a test message directly to the pipeline — no WhatsApp needed.

    Example:
        curl -X POST http://localhost:8000/simulate \\
             -H "Content-Type: application/json" \\
             -d '{"customer_number": "919999999999", "message": "Do you have laptop bags?"}'
    """
    result = process_message(payload.customer_number, payload.message, db)
    return WebhookResponse(
        status="ok",
        intent=result["intent"],
        reply=result["reply"],
    )


# ─── Admin read endpoints ─────────────────────────────────────────────────────

@router.get("/messages")
async def list_messages(limit: int = 50, db: Session = Depends(get_db)):
    """Return recent message logs."""
    messages = get_recent_messages(db, limit=limit)
    count = get_message_count(db)
    return {"total": count, "messages": messages}


@router.get("/products")
async def list_products(db: Session = Depends(get_db)):
    """Return all products."""
    return {"products": get_all_products(db)}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SupportBot MSME"}
