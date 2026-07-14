"""
predict.py

Run inference using trained YOLO model.

Author:
Shikhar Chauhan
"""

import sys
from pathlib import Path

# ==========================================================
# Fix Python Imports
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT))

# ==========================================================

from ultralytics import YOLO
from utils.crop_receipt import crop_receipt

# ==========================================================
# Paths
# ==========================================================

MODEL_PATH = (
    PROJECT_ROOT
    / "runs"
    / "detect"
    / "receipt_detector_v2"
    / "weights"
    / "best.pt"
)

IMAGE_FOLDER = (
    PROJECT_ROOT
    / "dataset"
    / "test"
    / "images"
)

OUTPUT_FOLDER = (
    PROJECT_ROOT
    / "outputs"
)

CROP_FOLDER = (
    PROJECT_ROOT
    / "outputs"
    / "crops"
)

# ==========================================================

print("=" * 60)
print("Retail Receipt Intelligence")
print("=" * 60)

print(f"Model : {MODEL_PATH}")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"\nModel not found:\n{MODEL_PATH}"
    )

print("Loading Model...")

model = YOLO(str(MODEL_PATH))

# ==========================================================
# Predict
# ==========================================================

results = model.predict(

    source=str(IMAGE_FOLDER),

    conf=0.25,

    save=True,

    project=str(OUTPUT_FOLDER),

    name="predictions",

    exist_ok=True

)

print("\nPrediction Finished\n")

# ==========================================================
# Crop Receipts
# ==========================================================

image_files = sorted(

    list(IMAGE_FOLDER.glob("*.jpg")) +
    list(IMAGE_FOLDER.glob("*.jpeg")) +
    list(IMAGE_FOLDER.glob("*.png"))

)

print("=" * 60)
print("Cropping Receipts")
print("=" * 60)

count = 0

for result, image_path in zip(results, image_files):

    crop = crop_receipt(

        result,

        image_path,

        CROP_FOLDER

    )

    if crop is not None:
        count += 1

print()

print("=" * 60)
print("Completed Successfully")
print("=" * 60)

print(f"Receipts Detected : {count}")
print(f"Predictions Saved : {OUTPUT_FOLDER/'predictions'}")
print(f"Crops Saved       : {CROP_FOLDER}")