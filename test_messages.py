"""
test_messages.py — Run sample test messages through SupportBot MSME locally.

Usage:
    python test_messages.py

The FastAPI server must be running:
    uvicorn app.main:app --reload
"""

import json
import requests

BASE_URL = "http://localhost:8000"

TEST_CASES = [
    {
        "label": "Greeting",
        "customer_number": "919876543210",
        "message": "Hi! Good morning.",
    },
    {
        "label": "Product Inquiry — Laptop Bag",
        "customer_number": "919876543210",
        "message": "Do you have laptop bags?",
    },
    {
        "label": "Price Inquiry — Wireless Mouse",
        "customer_number": "919812345678",
        "message": "How much does the wireless mouse cost?",
    },
    {
        "label": "Stock Inquiry — Keyboard",
        "customer_number": "919888888888",
        "message": "Is the mechanical keyboard available?",
    },
    {
        "label": "Order Status — by ID",
        "customer_number": "919876543210",
        "message": "Can you check my order ORD-1001?",
    },
    {
        "label": "Order Status — latest order",
        "customer_number": "919812345678",
        "message": "Where is my order? When will it be delivered?",
    },
    {
        "label": "Unknown / out of scope",
        "customer_number": "919900000000",
        "message": "Can you book a taxi for me?",
    },
    {
        "label": "Product not in catalogue",
        "customer_number": "919900000001",
        "message": "Do you sell gaming chairs?",
    },
]


def run_tests():
    print("=" * 60)
    print("SupportBot MSME — Test Suite")
    print("=" * 60)

    passed = 0
    failed = 0

    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}] {case['label']}")
        print(f"    Customer : {case['customer_number']}")
        print(f"    Message  : {case['message']}")

        try:
            resp = requests.post(
                f"{BASE_URL}/simulate",
                json={
                    "customer_number": case["customer_number"],
                    "message": case["message"],
                },
                timeout=30,
            )
            data = resp.json()
            print(f"    Intent   : {data.get('intent', 'N/A')}")
            print(f"    Reply    : {data.get('reply', 'N/A')}")
            passed += 1

        except requests.ConnectionError:
            print("    ERROR: Could not connect. Is the server running?")
            failed += 1
        except Exception as exc:
            print(f"    ERROR: {exc}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
