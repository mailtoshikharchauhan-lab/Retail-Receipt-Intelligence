"""
receipts.py

Receipt API Routes

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""
import traceback
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status
)

from sqlalchemy.orm import Session

from api.database.database import get_db
from api.database import crud

from api.schemas import (
    ReceiptResponse,
    ReceiptUploadResponse,
    ReceiptListResponse,
    ErrorResponse,
)

from api.services.detection_service import DetectionService
from api.services.ocr_service import OCRService
from api.services.parser_service import ParserService
from api.services.database_service import DatabaseService
from api.services.confidence_service import ConfidenceService
from api.services.receipt_service import ReceiptService

from pathlib import Path

# =========================================================

router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"],
)

# =========================================================
# Dependency
# =========================================================

MODEL_PATH = Path("models") / "best.pt"


def get_receipt_service(db: Session):

    detection_service = DetectionService(MODEL_PATH)

    ocr_service = OCRService()

    parser_service = ParserService()

    database_service = DatabaseService(db)

    confidence_service = ConfidenceService()

    return ReceiptService(

        detection_service,

        ocr_service,

        parser_service,

        database_service,

        confidence_service,

    )


# =========================================================
# Upload Receipt
# =========================================================

@router.post(
    "/upload",
    response_model=ReceiptUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    try:

        service = get_receipt_service(db)

        receipt = service.process_receipt(file)

        return {
            "success": True,
            "message": "Receipt processed successfully.",
            "receipt": receipt
        }

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# Get All Receipts
# =========================================================

@router.get(
    "/",
    response_model=ReceiptListResponse,
)

def get_receipts(
    db: Session = Depends(get_db),
):

    receipts = crud.get_all_receipts(db)

    return {
    "total_receipts": len(receipts),
    "receipts": receipts
}


# =========================================================
# Get One Receipt
# =========================================================

@router.get(
    "/{receipt_id}",
    response_model=ReceiptResponse,
)

def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
):

    receipt = crud.get_receipt(

        db,

        receipt_id

    )

    if receipt is None:

        raise HTTPException(

            status_code=404,

            detail="Receipt not found."

        )

    return receipt

# =========================================================
# Delete Receipt
# =========================================================

@router.delete(
    "/{receipt_id}",
)

def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
):

    deleted = crud.delete_receipt(

        db,

        receipt_id

    )

    if not deleted:

        raise HTTPException(

            status_code=404,

            detail="Receipt not found."

        )

    return {

        "success": True,

        "message": "Receipt deleted successfully."

    }