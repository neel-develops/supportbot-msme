"""
SupportBot MSME — FastAPI Application Entry Point
Serves the React frontend and the API.
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database.db import init_db
from app.routes import router

# Load environment variables
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SupportBot MSME...")
    init_db()
    logger.info("Database initialised. Server ready.")
    yield
    logger.info("Shutting down SupportBot MSME.")


app = FastAPI(
    title="SupportBot MSME",
    description="AI-powered WhatsApp customer support automation for small businesses.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)

# Serve React frontend if built
if FRONTEND_DIST.exists():
    assets_path = FRONTEND_DIST / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

    @app.get("/dashboard/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        index = FRONTEND_DIST / "index.html"
        return FileResponse(str(index))

    @app.get("/dashboard", include_in_schema=False)
    async def serve_dashboard_root():
        return FileResponse(str(FRONTEND_DIST / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
