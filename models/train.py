"""
train.py

Train YOLO11 Receipt Detector

Author:
Shikhar Chauhan
"""

from pathlib import Path
from ultralytics import YOLO

# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_YAML = PROJECT_ROOT / "dataset" / "data.yaml"

# ==========================================================
# YOLO Training Configuration
# ==========================================================

MODEL = "yolo11s.pt"

EPOCHS = 30

IMAGE_SIZE = 640

BATCH_SIZE = 8

DEVICE = "cpu"          # Change to "0" when using GPU

WORKERS = 2

PATIENCE = 10

OPTIMIZER = "AdamW"

PROJECT_NAME = "runs/detect"

EXPERIMENT_NAME = "receipt_detector_v2"

CACHE = False

SAVE_PLOTS = True

VERBOSE = True

SAVE_MODEL = True

EXIST_OK = True

# ==========================================================
# Display Configuration
# ==========================================================

print("=" * 60)
print("Retail Receipt Intelligence")
print("=" * 60)

print(f"Model           : {MODEL}")
print(f"Dataset         : {DATA_YAML}")
print(f"Epochs          : {EPOCHS}")
print(f"Image Size      : {IMAGE_SIZE}")
print(f"Batch Size      : {BATCH_SIZE}")
print(f"Device          : {DEVICE}")
print(f"Workers         : {WORKERS}")
print(f"Optimizer       : {OPTIMIZER}")
print(f"Patience        : {PATIENCE}")

print("=" * 60)

# ==========================================================
# Load Model
# ==========================================================

model = YOLO(MODEL)

# ==========================================================
# Train
# ==========================================================

results = model.train(

    data=str(DATA_YAML),

    epochs=EPOCHS,

    imgsz=IMAGE_SIZE,

    batch=BATCH_SIZE,

    device=DEVICE,

    workers=WORKERS,

    optimizer=OPTIMIZER,

    patience=PATIENCE,

    project=PROJECT_NAME,

    name=EXPERIMENT_NAME,

    cache=CACHE,

    plots=SAVE_PLOTS,

    verbose=VERBOSE,

    save=SAVE_MODEL,

    exist_ok=EXIST_OK

)

# ==========================================================
# Finish
# ==========================================================

BEST_MODEL = (
    PROJECT_ROOT
    / "runs"
    / "detect"
    / EXPERIMENT_NAME
    / "weights"
    / "best.pt"
)

LAST_MODEL = (
    PROJECT_ROOT
    / "runs"
    / "detect"
    / EXPERIMENT_NAME
    / "weights"
    / "last.pt"
)

print("\n" + "=" * 60)
print("Training Completed Successfully")
print("=" * 60)

print(f"\nBest Model : {BEST_MODEL}")
print(f"Last Model : {LAST_MODEL}")