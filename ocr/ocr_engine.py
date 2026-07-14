"""
ocr_engine.py

Receipt OCR using EasyOCR

Author:
Shikhar Chauhan
"""

import sys
import tempfile
from pathlib import Path

import cv2
import easyocr
import numpy as np

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from utils.preprocess import preprocess_receipt

# ==========================================================

print("Loading EasyOCR model...")

reader = easyocr.Reader(
    ["en"],
    gpu=False
)

# ==========================================================

def read_receipt(image_path, low_text=0.4, text_threshold=0.7, preprocess_mode='standard'):
    """
    Read receipt text using EasyOCR.
    
    Args:
        image_path: Path to receipt image
        low_text: Lower bound for text region detection (default 0.4).
                  Lower values increase sensitivity to faint text.
        text_threshold: Threshold for character recognition (default 0.7).
                        Lower values accept more uncertain characters.
        preprocess_mode: Preprocessing mode - 'standard' (default), 'auto', 'faded', 
                        'shadow', 'wrinkled', 'perspective', 'aggressive'
    
    Open problem investigation (root cause #7 continuation):
    Even with canvas_size=3600 and mag_ratio=1.5, some receipts still
    show partial price truncation. These parameters tune EasyOCR's
    detection sensitivity to help recover faint/small text.
    """
    
    # Choose preprocessing method
    if preprocess_mode == 'standard':
        # Use standard preprocessing
        processed = preprocess_receipt(image_path)
        if processed.ndim == 3:

            if processed.shape[2] == 1:
                processed = np.squeeze(processed, axis=2)

            elif processed.shape[2] == 3:
                processed = cv2.cvtColor(
                    processed,
                    cv2.COLOR_BGR2GRAY
                )
    else:
        # Use advanced preprocessing
        from utils.advanced_preprocess import preprocess_receipt_advanced
        processed = preprocess_receipt_advanced(image_path, mode=preprocess_mode)
        if processed.ndim == 3:

            if processed.shape[2] == 1:
                processed = np.squeeze(processed, axis=2)

            elif processed.shape[2] == 3:
                processed = cv2.cvtColor(
                    processed,
                    cv2.COLOR_BGR2GRAY
                )

    processed = np.asarray(processed)

    if processed.ndim == 3:

        if processed.shape[2] == 1:
            processed = processed[:, :, 0]

        else:
            processed = cv2.cvtColor(
                processed,
                cv2.COLOR_BGR2GRAY
            )

    results = reader.readtext(
        processed,
        detail=1,
        paragraph=False,
        canvas_size=2048,
        mag_ratio=1.0,
        low_text=0.4,
        text_threshold=0.7
    )

    output = []

    for item in results:

        output.append(
            {
                "text": item[1],
                "confidence": float(item[2]),
                "box": item[0]
            }
        )

    return output