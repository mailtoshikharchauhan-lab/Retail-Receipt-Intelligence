"""
schemas.py

Pydantic Schemas

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Receipt Item
# ==========================================================

class ReceiptItemResponse(BaseModel):
    """
    Receipt Item Response
    """

    id: Optional[int] = None

    item_name: str

    quantity: float = 1

    price: float

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# Receipt Response
# ==========================================================

class ReceiptResponse(BaseModel):
    """
    Complete Receipt Response
    """

    id: Optional[int] = None

    store: Optional[str] = None

    date: Optional[str] = None

    time: Optional[str] = None

    subtotal: Optional[float] = None

    tax: Optional[float] = None

    total: Optional[float] = None

    payment_method: Optional[str] = None

    confidence_score: float = 0

    confidence_level: str = "LOW"

    processing_status: str = "Needs Review"

    image_path: Optional[str] = None

    crop_path: Optional[str] = None

    json_path: Optional[str] = None

    ocr_engine: Optional[str] = None

    model_version: Optional[str] = None

    created_at: Optional[datetime] = None

    items: List[ReceiptItemResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# Upload Response
# ==========================================================

class ReceiptUploadResponse(BaseModel):

    success: bool

    message: str

    receipt: ReceiptResponse


# ==========================================================
# Receipt List
# ==========================================================

class ReceiptListResponse(BaseModel):

    total_receipts: int

    receipts: List[ReceiptResponse]


# ==========================================================
# Analytics
# ==========================================================

class AnalyticsResponse(BaseModel):

    total_receipts: int

    total_amount: float

    average_total: float

    average_confidence: float

    high_confidence: int

    medium_confidence: int

    low_confidence: int

    needs_review: int


# ==========================================================
# Health
# ==========================================================

class HealthResponse(BaseModel):

    status: str

    version: str

    database: str


# ==========================================================
# Error
# ==========================================================

class ErrorResponse(BaseModel):

    success: bool = False

    error: str

    details: Optional[str] = None