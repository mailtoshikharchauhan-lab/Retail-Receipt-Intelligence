"""
confidence_service.py

Confidence Scoring Service

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ConfidenceResult:
    score: float
    level: str
    status: str
    breakdown: Dict


class ConfidenceService:
    """
    Calculates receipt confidence.

    Version 1

    Rule Based Confidence
    """

    REQUIRED_FIELDS = [

        "store",

        "date",

        "time",

        "total"

    ]

    OPTIONAL_FIELDS = [

        "subtotal",

        "tax",

        "payment_method"

    ]

    # -----------------------------------------------------

    def calculate(

        self,

        receipt: dict,

        yolo_confidence: float = 1.0,

        ocr_confidence: float = 1.0

    ) -> ConfidenceResult:

        score = 0

        breakdown = {}

        # ---------------------------------------------
        # YOLO
        # ---------------------------------------------

        yolo_score = yolo_confidence * 20

        score += yolo_score

        breakdown["yolo"] = round(yolo_score, 2)

        # ---------------------------------------------
        # OCR
        # ---------------------------------------------

        ocr_score = ocr_confidence * 30

        score += ocr_score

        breakdown["ocr"] = round(ocr_score, 2)

        # ---------------------------------------------
        # Mandatory Fields
        # ---------------------------------------------

        mandatory_found = 0

        for field in self.REQUIRED_FIELDS:

            if receipt.get(field):

                mandatory_found += 1

        mandatory_score = (

            mandatory_found /

            len(self.REQUIRED_FIELDS)

        ) * 30

        score += mandatory_score

        breakdown["mandatory"] = round(

            mandatory_score,

            2

        )

        # ---------------------------------------------
        # Items
        # ---------------------------------------------

        items = receipt.get(

            "items",

            []

        )

        item_score = 10 if len(items) > 0 else 0

        score += item_score

        breakdown["items"] = item_score

        # ---------------------------------------------
        # Optional Fields
        # ---------------------------------------------

        optional = 0

        for field in self.OPTIONAL_FIELDS:

            if receipt.get(field):

                optional += 1

        optional_score = (

            optional /

            len(self.OPTIONAL_FIELDS)

        ) * 10

        score += optional_score

        breakdown["optional"] = round(

            optional_score,

            2

        )

        score = round(score, 2)

        # ---------------------------------------------
        # Level
        # ---------------------------------------------

        if score >= 90:

            level = "HIGH"

            status = "Processed"

        elif score >= 70:

            level = "MEDIUM"

            status = "Needs Review"

        else:

            level = "LOW"

            status = "Rejected"

        return ConfidenceResult(

            score=score,

            level=level,

            status=status,

            breakdown=breakdown

        )