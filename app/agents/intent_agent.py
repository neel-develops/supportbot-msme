"""
Intent Detection Agent.

Uses OpenAI to classify customer messages into one of:
  - greeting
  - product_inquiry
  - price_inquiry
  - order_status
  - unknown

Returns a structured dict:
  {
    "intent": "product_inquiry",
    "product_name": "Laptop Bag",   # populated when relevant
    "order_id": None,
    "confidence": "high"
  }
"""

import json
import logging
import os
from typing import Optional

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")
        _client = OpenAI(api_key=api_key)
    return _client


SYSTEM_PROMPT = """
You are an intent classifier for a WhatsApp customer support bot for a small electronics and accessories shop.

Classify the user's message into EXACTLY ONE of these intents:
- greeting         : Hello, Hi, Hey, Good morning, etc.
- product_inquiry  : Asking if a product is available or in stock
- price_inquiry    : Asking about the price or cost of a product
- order_status     : Asking about their order, delivery, tracking
- unknown          : Anything that does not fit the above

Also extract:
- product_name : the product mentioned (null if none)
- order_id     : the order ID mentioned e.g. ORD-1001 (null if none)

Respond with ONLY valid JSON. No explanation. No markdown. Example:
{"intent": "product_inquiry", "product_name": "Laptop Bag", "order_id": null, "confidence": "high"}
""".strip()


def detect_intent(message: str) -> dict:
    """
    Classify a customer message and extract entities.

    Args:
        message: Raw customer message text.

    Returns:
        dict with keys: intent, product_name, order_id, confidence
    """
    fallback = {
        "intent": "unknown",
        "product_name": None,
        "order_id": None,
        "confidence": "low",
    }

    if not message or not message.strip():
        return fallback

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.strip()},
            ],
            temperature=0,
            max_tokens=120,
        )

        raw = response.choices[0].message.content.strip()
        logger.debug("Intent raw response: %s", raw)

        result = json.loads(raw)

        # Validate intent is one of the known values
        valid_intents = {"greeting", "product_inquiry", "price_inquiry", "order_status", "unknown"}
        if result.get("intent") not in valid_intents:
            logger.warning("Unknown intent returned: %s — defaulting to unknown", result.get("intent"))
            result["intent"] = "unknown"

        return {
            "intent": result.get("intent", "unknown"),
            "product_name": result.get("product_name"),
            "order_id": result.get("order_id"),
            "confidence": result.get("confidence", "medium"),
        }

    except (OpenAIError, json.JSONDecodeError, KeyError) as exc:
        logger.error("Intent detection failed: %s", exc)
        return fallback
