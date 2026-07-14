"""
preprocess.py

Preprocess receipt image before OCR.

NOTE: EasyOCR's recognizer is a deep model trained on natural,
continuous-tone text (unlike Tesseract, which wants clean black/white
input). Hard adaptive-threshold binarization tends to HURT EasyOCR --
it destroys thin digit strokes and causes misreads. This version
keeps the image grayscale and only lightly enhances contrast.

Author:
Shikhar Chauhan
"""

from pathlib import Path

import cv2
import numpy as np


def deskew(image, max_angle=25):
    """
    Detects and corrects rotation in a cropped receipt image.

    crop_receipt.py only produces an axis-aligned bounding-box crop --
    if the original photo was taken at an angle, the receipt itself
    stays tilted inside that crop. A tilted receipt breaks our
    y-coordinate based line grouping (words on the same physical line
    end up at different y-values depending on how far right they are),
    which fragments or drops whole rows of text.

    Uses the minimum-area rectangle of the dark (text/paper-edge)
    pixels to estimate rotation, then rotates the image to level it.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Text/paper is dark relative to a bright background in most
    # receipt photos -- invert so "content" pixels are non-zero.
    inverted = cv2.bitwise_not(gray)

    thresh = cv2.threshold(
        inverted,
        0,
        255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )[1]

    coords = np.column_stack(np.where(thresh > 0))

    if coords.shape[0] < 50:
        # Not enough signal to estimate an angle safely -- skip.
        return image

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Guard against wild misfires (e.g. a near-square text mask
    # confusing minAreaRect) -- only correct plausible photo tilts.
    if abs(angle) < 0.5 or abs(angle) > max_angle:
        return image

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    rotated = cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return rotated


def preprocess_receipt(image_path, output_path=None, binarize=False):
    """
    Enhance receipt image for OCR.

    Args:
        image_path : Path to cropped receipt
        output_path : Optional path to save processed image
        binarize : If True, applies adaptive threshold (old behavior).
                    Leave False for EasyOCR.

    Returns:
        Processed image (numpy array)
    """

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Straighten tilted photos BEFORE anything else -- line grouping
    # downstream assumes horizontal rows.
    image = deskew(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.fastNlMeansDenoising(gray, h=7)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    processed = clahe.apply(gray)

    if binarize:
        processed = cv2.adaptiveThreshold(
            processed,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15
        )

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), processed)

    return processed