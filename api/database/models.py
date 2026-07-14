"""
models.py

SQLAlchemy ORM Models

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from api.database.database import Base


# ==========================================================
# Receipt Table
# ==========================================================

class Receipt(Base):
    """
    Main receipt table.
    """

    __tablename__ = "receipts"

    # ------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------

    id = Column(Integer, primary_key=True, index=True)

    # ------------------------------------------------------
    # Receipt Information
    # ------------------------------------------------------

    store = Column(String(255), nullable=True)

    date = Column(String(50), nullable=True)

    time = Column(String(50), nullable=True)

    subtotal = Column(Float, nullable=True)

    tax = Column(Float, nullable=True)

    total = Column(Float, nullable=True)

    payment_method = Column(String(100), nullable=True)

    # ------------------------------------------------------
    # Confidence
    # ------------------------------------------------------

    confidence_score = Column(Float, default=0.0)

    confidence_level = Column(String(20), default="LOW")

    processing_status = Column(
        String(50),
        default="Needs Review"
    )

    # ------------------------------------------------------
    # AI Metadata
    # ------------------------------------------------------

    ocr_engine = Column(
        String(100),
        default="EasyOCR"
    )

    model_version = Column(
        String(100),
        default="YOLO11s_v2"
    )

    # ------------------------------------------------------
    # File Paths
    # ------------------------------------------------------

    image_path = Column(String(500), nullable=True)

    crop_path = Column(String(500), nullable=True)

    json_path = Column(String(500), nullable=True)

    # ------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # ------------------------------------------------------
    # Relationship
    # ------------------------------------------------------

    items = relationship(
        "ReceiptItem",
        back_populates="receipt",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    # ------------------------------------------------------

    def __repr__(self):

        return (
            f"<Receipt("
            f"id={self.id}, "
            f"store={self.store}, "
            f"total={self.total})>"
        )


# ==========================================================
# Receipt Items Table
# ==========================================================

class ReceiptItem(Base):
    """
    Stores all purchased items.
    """

    __tablename__ = "receipt_items"

    # ------------------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    receipt_id = Column(
        Integer,
        ForeignKey(
            "receipts.id",
            ondelete="CASCADE"
        )
    )

    item_name = Column(
        String(255),
        nullable=False
    )

    quantity = Column(
        Float,
        default=1
    )

    price = Column(
        Float,
        nullable=False
    )

    # ------------------------------------------------------

    receipt = relationship(
        "Receipt",
        back_populates="items"
    )

    # ------------------------------------------------------

    def __repr__(self):

        return (
            f"<ReceiptItem("
            f"id={self.id}, "
            f"name={self.item_name}, "
            f"price={self.price})>"
        )