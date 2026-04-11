# SupportBot MSME

AI-powered WhatsApp customer support automation for small businesses.

```
Customer WhatsApp → FastAPI Backend → Intent Agent (OpenAI) → DB Lookup → Response Agent → Reply
                                                                              ↓
                                                                     Streamlit Dashboard
```

---

## Project Structure

```
supportbot-msme/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── routes.py                # All API endpoints
│   ├── agents/
│   │   ├── intent_agent.py      # OpenAI intent classification
│   │   └── response_agent.py    # OpenAI response generation
│   ├── database/
│   │   ├── db.py                # Engine, session, seed data
│   │   └── models.py            # SQLAlchemy ORM models
│   └── services/
│       ├── product_service.py   # Product lookup + CRUD
│       ├── order_service.py     # Order lookup
│       └── message_service.py   # Conversation logging
├── dashboard/
│   └── dashboard.py             # Streamlit admin dashboard
├── test_messages.py             # Local test runner
├── .env                         # Environment variables (do not commit)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone <your-repo>
cd supportbot-msme

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Edit `.env`:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_VERIFY_TOKEN=supportbot_verify_token
```

Get your OpenAI API key at: https://platform.openai.com/api-keys

---

## Running the Application

### Terminal 1 — Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

Server starts at: http://localhost:8000
Interactive API docs: http://localhost:8000/docs

### Terminal 2 — Start the Streamlit dashboard

```bash
streamlit run dashboard/dashboard.py
```

Dashboard opens at: http://localhost:8501

---

## Testing Without WhatsApp

Use the `/simulate` endpoint to test the full pipeline locally:

### Via curl

```bash
# Greeting
curl -X POST http://localhost:8000/simulate \
     -H "Content-Type: application/json" \
     -d '{"customer_number": "919999999999", "message": "Hi there!"}'

# Product inquiry
curl -X POST http://localhost:8000/simulate \
     -H "Content-Type: application/json" \
     -d '{"customer_number": "919999999999", "message": "Do you have laptop bags?"}'

# Price check
curl -X POST http://localhost:8000/simulate \
     -H "Content-Type: application/json" \
     -d '{"customer_number": "919999999999", "message": "How much is the wireless mouse?"}'

# Order status
curl -X POST http://localhost:8000/simulate \
     -H "Content-Type: application/json" \
     -d '{"customer_number": "919999999999", "message": "Where is my order ORD-1001?"}'
```

### Via Python test script

```bash
python test_messages.py
```

### Via Streamlit dashboard

Open http://localhost:8501 → navigate to **Test Bot**

---

## API Endpoints

| Method | Endpoint      | Description                                  |
|--------|---------------|----------------------------------------------|
| GET    | `/health`     | Health check                                 |
| GET    | `/webhook`    | WhatsApp webhook verification                |
| POST   | `/webhook`    | Receive inbound WhatsApp messages            |
| POST   | `/simulate`   | Test pipeline without WhatsApp               |
| GET    | `/messages`   | List recent conversation logs                |
| GET    | `/products`   | List all products                            |

---

## WhatsApp Cloud API Setup (Production)

1. Create a Meta Developer account at https://developers.facebook.com
2. Create an app → Add WhatsApp product
3. Get your **Phone Number ID** and **Access Token**
4. Set your webhook URL to: `https://your-domain.com/webhook`
5. Set **Verify Token** to match `WHATSAPP_VERIFY_TOKEN` in `.env`
6. For local development, use [ngrok](https://ngrok.com):

```bash
ngrok http 8000
# Use the https URL as your webhook URL in Meta dashboard
```

---

## Sample Products (Pre-seeded)

| Product             | Price   | Stock |
|---------------------|---------|-------|
| Laptop Bag          | ₹999    | 5     |
| Wireless Mouse      | ₹499    | 20    |
| Mechanical Keyboard | ₹1,999  | 8     |
| USB-C Hub           | ₹1,299  | 15    |
| Monitor Stand       | ₹799    | 12    |

---

## Sample Orders (Pre-seeded)

| Order ID  | Customer      | Status            | Delivery    |
|-----------|---------------|-------------------|-------------|
| ORD-1001  | Rahul Sharma  | Out for delivery  | 13 Apr 2026 |
| ORD-1002  | Priya Mehta   | Delivered         | 10 Apr 2026 |
| ORD-1003  | Arjun Patel   | Processing        | 15 Apr 2026 |

---

## Deployment (Cloud)

### Backend — Render / Railway

1. Push to GitHub
2. Connect repo to [Render](https://render.com) or [Railway](https://railway.app)
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in the platform dashboard

### Dashboard — Streamlit Cloud

1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. Deploy `dashboard/dashboard.py`
4. Add secrets in Streamlit Cloud settings

---

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python, FastAPI         |
| AI         | OpenAI GPT-3.5-turbo    |
| Database   | SQLite + SQLAlchemy ORM |
| Dashboard  | Streamlit               |
| Messaging  | WhatsApp Cloud API      |
| Config     | python-dotenv, Pydantic |
