"""
receipt_service.py

Main AI Pipeline

Author: Shikhar Chauhan
"""
import cv2
from pathlib import Path
import shutil
import logging
from uuid import uuid4

from api.services.detection_service import DetectionService
from api.services.ocr_service import OCRService
from api.services.parser_service import ParserService
from api.services.database_service import DatabaseService
from api.services.confidence_service import ConfidenceService
from ocr.ocr_engine import read_receipt
from utils.save_json import save_json


logger = logging.getLogger(__name__)


class ReceiptService:

    def __init__(

        self,

        detection_service: DetectionService,

        ocr_service: OCRService,

        parser_service: ParserService,

        database_service: DatabaseService,

        confidence_service: ConfidenceService

    ):

        self.detector = detection_service

        self.ocr = ocr_service

        self.parser = parser_service

        self.database = database_service

        self.confidence = confidence_service

    # =====================================================

    def process_receipt(

        self,

        uploaded_file

    ):

        logger.info("Starting receipt pipeline...")

        image_path = self._save_upload(

            uploaded_file

        )

        crop_path = self.detector.process(

            image_path

        )

        print("=" * 60)
        print("Crop Path :", crop_path)
        print("Exists    :", crop_path.exists())

        img = cv2.imread(str(crop_path))

        if img is None:
            print("OpenCV could not read crop!")
        else:
            print("Crop Shape:", img.shape)
            print("Crop Type :", img.dtype)

        print("=" * 60)
        if crop_path is None:

            raise Exception(

                "Receipt not detected."

            )

        

        ocr_result = read_receipt(
        crop_path,
        preprocess_mode="faded"
        )

        receipt = self.parser.process(

            ocr_result

        )

        confidence = self.confidence.calculate(

            receipt

        )

        receipt["confidence_score"] = (

            confidence.score

        )

        receipt["confidence_level"] = (

            confidence.level

        )

        receipt["processing_status"] = (

            confidence.status

        )

        receipt["image_path"] = str(

            image_path

        )

        receipt["crop_path"] = str(

            crop_path

        )

        json_path = save_json(

            receipt,

            crop_path.stem + ".json"

        )

        receipt["json_path"] = str(

            json_path

        )

        db_receipt = self.database.save_receipt(

            receipt

        )

        logger.info(

            "Receipt processed successfully."

        )

        return db_receipt

    # =====================================================

    def _save_upload(

        self,

        uploaded_file

    ) -> Path:

        uploads = Path("uploads")

        uploads.mkdir(

            exist_ok=True

        )

        filename = (

            uuid4().hex +

            Path(uploaded_file.filename).suffix

        )

        destination = uploads / filename

        with open(

            destination,

            "wb"

        ) as buffer:

            shutil.copyfileobj(

                uploaded_file.file,

                buffer

            )

        logger.info(

            f"Upload saved: {destination}"

        )

        return destination