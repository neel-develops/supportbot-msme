"""
Response Generator Agent.

Takes intent + context data and uses OpenAI to generate a natural,
friendly WhatsApp reply for the customer.
"""

import logging
import os
from typing import Optional

from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)

_client: Optional[OpenAI] = None

BUSINESS_NAME = "TechShop MSME"


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def _build_system_prompt() -> str:
    return f"""
You are a friendly, helpful WhatsApp customer support agent for {BUSINESS_NAME}, 
a small electronics and accessories shop.

Rules:
- Keep replies short (2-4 lines max).
- Be warm and professional.
- Use ₹ for prices.
- If a product is out of stock, apologise and offer to notify when available.
- If you don't know something, say "Let me check and get back to you."
- Do NOT use markdown formatting like ** or ##.
- Do NOT add greetings like "Dear Customer" — go straight to the point.
""".strip()


def generate_response(intent: str, context: dict, customer_message: str) -> str:
    """
    Generate a customer-facing reply based on detected intent and context data.

    Args:
        intent: Detected intent string.
        context: Dict containing product info, order info, etc.
        customer_message: Original customer message (for tone matching).

    Returns:
        A natural language reply string.
    """
    user_prompt = _build_user_prompt(intent, context, customer_message)

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": _build_system_prompt()},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=200,
        )
        reply = response.choices[0].message.content.strip()
        logger.info("Generated reply for intent '%s': %s", intent, reply[:80])
        return reply

    except OpenAIError as exc:
        logger.error("Response generation failed: %s", exc)
        return (
            "Sorry, I'm having trouble processing your request right now. "
            "Please try again in a moment or contact us directly."
        )


def _build_user_prompt(intent: str, context: dict, customer_message: str) -> str:
    """Build the GPT user prompt based on intent and available context data."""

    if intent == "greeting":
        return (
            f"Customer said: '{customer_message}'\n"
            "Greet them warmly and let them know you can help with product availability, "
            "pricing, and order status."
        )

    if intent in ("product_inquiry", "price_inquiry"):
        product = context.get("product")
        if product:
            stock_status = (
                f"In stock: {product['stock']} units"
                if product["stock"] > 0
                else "Currently out of stock"
            )
            return (
                f"Customer asked: '{customer_message}'\n"
                f"Product details:\n"
                f"  Name: {product['name']}\n"
                f"  Price: ₹{product['price']:.0f}\n"
                f"  Stock: {stock_status}\n"
                f"  Description: {product.get('description', '')}\n"
                "Generate a helpful reply."
            )
        else:
            product_name = context.get("product_name", "that product")
            return (
                f"Customer asked about '{product_name}' but it was not found in our catalog.\n"
                "Apologise and offer to help find a similar product or check later."
            )

    if intent == "order_status":
        order = context.get("order")
        if order:
            return (
                f"Customer asked: '{customer_message}'\n"
                f"Order details:\n"
                f"  Order ID: {order['order_id']}\n"
                f"  Product: {order['product_name']}\n"
                f"  Status: {order['status']}\n"
                f"  Expected delivery: {order.get('delivery_date', 'TBD')}\n"
                "Give a clear, reassuring status update."
            )
        else:
            order_id = context.get("order_id", "")
            return (
                f"Customer asked about order '{order_id}' but no matching order was found.\n"
                "Apologise and ask them to double-check the order ID or contact support."
            )

    # Fallback for unknown intent
    return (
        f"Customer said: '{customer_message}'\n"
        "You could not understand their request clearly. "
        "Politely ask them to clarify or offer to connect them with a human agent."
    )
