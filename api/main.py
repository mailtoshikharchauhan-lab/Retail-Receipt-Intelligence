"""
main.py

FastAPI Entry Point

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

import logging

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database.database import (
    create_database,
)

from api.routes.receipts import router as receipt_router
from api.routes.analytics import router as analytics_router

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Startup / Shutdown
# ---------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("===================================")
    logger.info("Retail Receipt Intelligence API")
    logger.info("Starting Server...")
    logger.info("===================================")

    create_database()

    logger.info("Database initialized.")

    model_path = Path("models") / "best.pt"

    if model_path.exists():

        logger.info("YOLO model found.")

    else:

        logger.warning("YOLO model not found.")

    yield

    logger.info("Shutting down API...")


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------

app = FastAPI(

    title="Retail Receipt Intelligence",

    description="AI Powered Receipt Intelligence System",

    version="1.0.0",

    lifespan=lifespan

)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(receipt_router)

app.include_router(analytics_router)

# ---------------------------------------------------------
# Health
# ---------------------------------------------------------


@app.get("/")

def root():

    return {

        "application": "Retail Receipt Intelligence",

        "status": "Running"

    }


@app.get("/health")

def health():

    return {

        "status": "Healthy",

        "version": "1.0.0"

    }