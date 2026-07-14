"""
evaluate.py

Evaluate trained YOLO model.

Author:
Shikhar Chauhan
"""

from ultralytics import YOLO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "runs" / "detect" / "runs" / "receipt_detector" / "weights" / "best.pt"

DATASET_YAML = PROJECT_ROOT / "dataset" / "dataset.yaml"

print("=" * 60)
print("Loading Model...")
print("=" * 60)

model = YOLO(str(MODEL_PATH))

metrics = model.val(data=str(DATASET_YAML))

print()
print("=" * 60)
print("Evaluation Results")
print("=" * 60)

print(f"mAP50      : {metrics.box.map50:.4f}")
print(f"mAP50-95   : {metrics.box.map:.4f}")
print(f"Precision  : {metrics.box.mp:.4f}")
print(f"Recall     : {metrics.box.mr:.4f}")