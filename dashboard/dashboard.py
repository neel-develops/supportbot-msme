"""
SupportBot MSME — Streamlit Admin Dashboard

Run with:
    streamlit run dashboard/dashboard.py
"""

import sys
import os

# Make sure the project root is on the path so app imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import streamlit as st
from datetime import datetime

from app.database.db import SessionLocal, init_db
from app.services.message_service import get_recent_messages, get_message_count
from app.services.product_service import get_all_products
from app.services.order_service import get_all_orders

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SupportBot MSME — Admin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── DB init ──────────────────────────────────────────────────────────────────
init_db()


@st.cache_data(ttl=15)
def load_messages(limit=200):
    db = SessionLocal()
    try:
        return get_recent_messages(db, limit=limit)
    finally:
        db.close()


@st.cache_data(ttl=30)
def load_products():
    db = SessionLocal()
    try:
        return get_all_products(db)
    finally:
        db.close()


@st.cache_data(ttl=30)
def load_orders():
    db = SessionLocal()
    try:
        return get_all_orders(db)
    finally:
        db.close()


@st.cache_data(ttl=15)
def load_message_count():
    db = SessionLocal()
    try:
        return get_message_count(db)
    finally:
        db.close()


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/chatbot.png", width=72)
    st.title("SupportBot MSME")
    st.caption("Admin Dashboard")
    st.divider()
    page = st.radio(
        "Navigate",
        ["📊 Overview", "💬 Conversations", "📦 Products", "🧾 Orders", "🧪 Test Bot"],
        label_visibility="collapsed",
    )
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}")


# ─── Overview ─────────────────────────────────────────────────────────────────
if page == "📊 Overview":
    st.title("📊 Overview")

    messages = load_messages()
    products = load_products()
    orders = load_orders()
    total_msgs = load_message_count()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Messages", total_msgs)
    col2.metric("Products Listed", len(products))
    col3.metric("Orders Tracked", len(orders))

    # Intent breakdown
    if messages:
        intents = [m.get("detected_intent") or "unknown" for m in messages]
        intent_counts = pd.Series(intents).value_counts().reset_index()
        intent_counts.columns = ["Intent", "Count"]
        col4.metric("Unique Customers", len({m["customer_number"] for m in messages}))

        st.divider()
        st.subheader("Intent Distribution")
        st.bar_chart(intent_counts.set_index("Intent"))
    else:
        col4.metric("Unique Customers", 0)
        st.info("No messages yet. Send a test message using the Test Bot page.")

    # Recent activity
    st.subheader("Recent Activity")
    if messages:
        recent = messages[:5]
        for msg in recent:
            with st.expander(f"📩 {msg['customer_number']} — {msg['timestamp'][:16]}"):
                st.markdown(f"**Customer:** {msg['message_text']}")
                st.markdown(f"**Bot:** {msg['bot_reply']}")
                st.caption(f"Intent: `{msg.get('detected_intent', 'unknown')}`")
    else:
        st.caption("No recent messages.")


# ─── Conversations ─────────────────────────────────────────────────────────────
elif page == "💬 Conversations":
    st.title("💬 Conversation Logs")

    messages = load_messages(200)

    if not messages:
        st.info("No conversations logged yet.")
    else:
        df = pd.DataFrame(messages)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp", ascending=False)

        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("🔍 Filter by customer number or message text")
        with col2:
            intent_filter = st.selectbox(
                "Filter by intent",
                ["All"] + sorted(df["detected_intent"].dropna().unique().tolist()),
            )

        if search:
            df = df[
                df["customer_number"].str.contains(search, case=False, na=False)
                | df["message_text"].str.contains(search, case=False, na=False)
            ]
        if intent_filter != "All":
            df = df[df["detected_intent"] == intent_filter]

        st.caption(f"Showing {len(df)} messages")

        for _, row in df.iterrows():
            with st.expander(
                f"📩 {row['customer_number']} | `{row.get('detected_intent', 'unknown')}` | {str(row['timestamp'])[:16]}"
            ):
                col_a, col_b = st.columns(2)
                col_a.markdown("**Customer message:**")
                col_a.info(row["message_text"])
                col_b.markdown("**Bot reply:**")
                col_b.success(row["bot_reply"])


# ─── Products ─────────────────────────────────────────────────────────────────
elif page == "📦 Products":
    st.title("📦 Product Catalogue")

    products = load_products()

    if not products:
        st.warning("No products in database.")
    else:
        df = pd.DataFrame(products)
        df["price"] = df["price"].apply(lambda x: f"₹{x:,.0f}")

        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(
                df[["name", "price", "stock", "description"]].rename(
                    columns={
                        "name": "Product",
                        "price": "Price",
                        "stock": "Stock",
                        "description": "Description",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        with col2:
            st.subheader("Stock Levels")
            stock_df = pd.DataFrame(products)[["name", "stock"]].set_index("name")
            st.bar_chart(stock_df)


# ─── Orders ───────────────────────────────────────────────────────────────────
elif page == "🧾 Orders":
    st.title("🧾 Orders")

    orders = load_orders()

    if not orders:
        st.info("No orders yet.")
    else:
        df = pd.DataFrame(orders)

        status_color = {
            "Delivered": "🟢",
            "Out for delivery": "🟡",
            "Processing": "🔵",
            "pending": "⚪",
        }

        for _, row in df.iterrows():
            icon = status_color.get(row["status"], "⚪")
            with st.expander(f"{icon} {row['order_id']} — {row['customer_name']} — {row['status']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Product", row["product_name"])
                c2.metric("Status", row["status"])
                c3.metric("Delivery", row.get("delivery_date") or "TBD")
                st.caption(f"Customer: {row['customer_number']}")


# ─── Test Bot ─────────────────────────────────────────────────────────────────
elif page == "🧪 Test Bot":
    st.title("🧪 Test Bot")
    st.caption("Send a test message directly through the processing pipeline — no WhatsApp needed.")

    import requests

    API_URL = st.text_input("API base URL", value="http://localhost:8000")
    customer_number = st.text_input("Simulated customer number", value="919999999999")

    st.subheader("Quick test messages")
    quick_msgs = [
        "Hi there!",
        "Do you have laptop bags?",
        "What is the price of the wireless mouse?",
        "Where is my order ORD-1001?",
        "Is the mechanical keyboard in stock?",
        "What products do you sell?",
    ]
    cols = st.columns(3)
    for i, qm in enumerate(quick_msgs):
        if cols[i % 3].button(qm, key=f"qm_{i}"):
            st.session_state["test_message"] = qm

    st.divider()
    user_message = st.text_area(
        "Or type your own message",
        value=st.session_state.get("test_message", ""),
        height=80,
    )

    if st.button("Send Message ↗", type="primary"):
        if not user_message.strip():
            st.warning("Please enter a message.")
        else:
            with st.spinner("Processing..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/simulate",
                        json={"customer_number": customer_number, "message": user_message},
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success("✅ Response received")
                        col1, col2 = st.columns(2)
                        col1.markdown("**Your message:**")
                        col1.info(user_message)
                        col2.markdown("**Bot reply:**")
                        col2.success(data["reply"])
                        st.caption(f"Detected intent: `{data['intent']}`")
                    else:
                        st.error(f"API error {resp.status_code}: {resp.text}")
                except requests.ConnectionError:
                    st.error(
                        "Could not connect to the API. Make sure the FastAPI server is running:\n\n"
                        "`uvicorn app.main:app --reload`"
                    )
