"""
crud.py

Database CRUD Operations

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from api.database.models import Receipt, ReceiptItem


# ==========================================================
# Helper
# ==========================================================

def to_float(value):
    """
    Safely convert OCR values to float.

    Returns:
        float | None
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value == "":
        return None

    value = value.replace(",", "")

    try:
        return float(value)
    except ValueError:
        return None


# ==========================================================
# CREATE
# ==========================================================

def create_receipt(
    db: Session,
    receipt_data: dict,
) -> Receipt:
    """
    Creates receipt and associated items.
    """

    receipt = Receipt(

        store=receipt_data.get("store"),

        date=receipt_data.get("date"),

        time=receipt_data.get("time"),

        subtotal=to_float(receipt_data.get("subtotal")),

        tax=to_float(receipt_data.get("tax")),

        total=to_float(receipt_data.get("total")),

        payment_method=receipt_data.get("payment_method"),

        confidence_score=receipt_data.get(
            "confidence_score",
            0
        ),

        confidence_level=receipt_data.get(
            "confidence_level",
            "LOW"
        ),

        processing_status=receipt_data.get(
            "processing_status",
            "Needs Review"
        ),

        image_path=receipt_data.get("image_path"),

        crop_path=receipt_data.get("crop_path"),

        json_path=receipt_data.get("json_path"),

        ocr_engine=receipt_data.get(
            "ocr_engine",
            "EasyOCR"
        ),

        model_version=receipt_data.get(
            "model_version",
            "YOLO11s_v2"
        )

    )

    db.add(receipt)

    db.flush()

    # ------------------------------------------------------
    # Save Items
    # ------------------------------------------------------

    for item in receipt_data.get("items", []):

        receipt_item = ReceiptItem(

            receipt_id=receipt.id,

            # parser uses "name"
            item_name=item.get("name", ""),

            quantity=to_float(
                item.get("quantity")
            ) or 1,

            price=to_float(
                item.get("price")
            ) or 0

        )

        db.add(receipt_item)

    db.commit()

    db.refresh(receipt)

    return receipt


# ==========================================================
# READ
# ==========================================================

def get_receipt(
    db: Session,
    receipt_id: int
) -> Optional[Receipt]:

    return (

        db.query(Receipt)

        .filter(
            Receipt.id == receipt_id
        )

        .first()

    )


def get_all_receipts(
    db: Session
) -> List[Receipt]:

    return (

        db.query(Receipt)

        .order_by(
            Receipt.created_at.desc()
        )

        .all()

    )


# ==========================================================
# UPDATE
# ==========================================================

def update_receipt_status(
    db: Session,
    receipt_id: int,
    status: str
):

    receipt = get_receipt(
        db,
        receipt_id
    )

    if receipt is None:
        return None

    receipt.processing_status = status

    db.commit()

    db.refresh(receipt)

    return receipt


# ==========================================================
# DELETE
# ==========================================================

def delete_receipt(
    db: Session,
    receipt_id: int
):

    receipt = get_receipt(
        db,
        receipt_id
    )

    if receipt is None:
        return False

    db.delete(receipt)

    db.commit()

    return True


# ==========================================================
# ANALYTICS
# ==========================================================

def get_analytics(
    db: Session
):

    total_receipts = db.query(
        Receipt
    ).count()

    total_amount = db.query(
        func.sum(
            Receipt.total
        )
    ).scalar()

    average_total = db.query(
        func.avg(
            Receipt.total
        )
    ).scalar()

    average_confidence = db.query(
        func.avg(
            Receipt.confidence_score
        )
    ).scalar()

    high_confidence = (

        db.query(Receipt)

        .filter(
            Receipt.confidence_level == "HIGH"
        )

        .count()

    )

    medium_confidence = (

        db.query(Receipt)

        .filter(
            Receipt.confidence_level == "MEDIUM"
        )

        .count()

    )

    low_confidence = (

        db.query(Receipt)

        .filter(
            Receipt.confidence_level == "LOW"
        )

        .count()

    )

    needs_review = (

        db.query(Receipt)

        .filter(
            Receipt.processing_status == "Needs Review"
        )

        .count()

    )

    return {

        "total_receipts": total_receipts,

        "total_amount": round(
            total_amount or 0,
            2
        ),

        "average_total": round(
            average_total or 0,
            2
        ),

        "average_confidence": round(
            average_confidence or 0,
            2
        ),

        "high_confidence": high_confidence,

        "medium_confidence": medium_confidence,

        "low_confidence": low_confidence,

        "needs_review": needs_review

    }


# ==========================================================
# SEARCH
# ==========================================================

def search_by_store(
    db: Session,
    store: str
):

    return (

        db.query(Receipt)

        .filter(
            Receipt.store.ilike(
                f"%{store}%"
            )
        )

        .all()

    )


def search_by_date(
    db: Session,
    date: str
):

    return (

        db.query(Receipt)

        .filter(
            Receipt.date == date
        )

        .all()

    )