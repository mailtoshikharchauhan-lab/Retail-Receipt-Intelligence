"""
detection_service.py

YOLO Receipt Detection Service

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

from pathlib import Path
from typing import Optional
import logging
from pathlib import Path
from ultralytics import YOLO

from utils.crop_receipt import crop_receipt


logger = logging.getLogger(__name__)


class DetectionService:
    """
    Wrapper around the YOLO receipt detector.
    """

    def __init__(self, model_path: Path):

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {self.model_path}"
            )

        logger.info("Loading YOLO model...")

        self.model = YOLO(str(self.model_path))

        logger.info("YOLO model loaded successfully.")

    # ----------------------------------------------------------

    def detect(
        self,
        image_path: Path
    ):
        """
        Run YOLO on an image.

        Returns
        -------
        Ultralytics Results object
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        logger.info("Running YOLO detection...")

        results = self.model.predict(

            source=str(image_path),

            conf=0.25,

            verbose=False

        )

        return results

    # ----------------------------------------------------------

    def crop_receipt(
        self,
        results,
        image_path: Path
    ) -> Optional[Path]:
        """
        Crops receipt using existing crop_receipt() utility.

        Returns
        -------
        Path to cropped receipt.
        """

        logger.info("Cropping receipt...")

        output_dir = Path("outputs") / "crops"

        crop_path = crop_receipt(
            results[0],          # First YOLO Result object
            image_path,
            output_dir
        )

        if crop_path is None:

            logger.warning("Receipt not detected.")

            return None

        logger.info(f"Cropped receipt saved to {crop_path}")

        return Path(crop_path)

    # ----------------------------------------------------------

    def process(
        self,
        image_path: Path
    ) -> Optional[Path]:
        """
        Complete detection pipeline.

        image

        ↓

        YOLO

        ↓

        Crop

        Returns crop path.
        """

        results = self.detect(image_path)

        crop = self.crop_receipt(

            results,

            image_path

        )

        return crop