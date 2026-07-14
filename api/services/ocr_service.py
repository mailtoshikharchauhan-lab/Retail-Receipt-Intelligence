"""
ocr_service.py

EasyOCR Service

Author: Shikhar Chauhan
"""

from pathlib import Path
import logging

from ocr.ocr_engine import read_receipt


logger = logging.getLogger(__name__)


class OCRService:
    """
    Wrapper around EasyOCR.

    NOTE:
    read_receipt() already performs preprocessing internally.
    Therefore this service should NOT preprocess again.
    """

    def __init__(self):

        logger.info("OCR Service initialized.")

    # ----------------------------------------------------------

    def extract_text(
        self,
        image_path: Path
    ):
        """
        Perform OCR.

        Parameters
        ----------
        image_path : Path
            Cropped receipt image.

        Returns
        -------
        list
            OCR output.
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        logger.info("Running OCR...")

        result = read_receipt(
        image_path,
        preprocess_mode="faded"
         )

        logger.info("OCR completed.")

        return result

    # ----------------------------------------------------------

    def process(
        self,
        image_path: Path
    ):
        """
        Complete OCR pipeline.

        Crop
          ↓
        EasyOCR
          ↓
        OCR Result
        """

        return self.extract_text(image_path)