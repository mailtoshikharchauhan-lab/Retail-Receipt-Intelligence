"""
verify_dataset.py

Verify YOLO dataset before training.

Author:
Shikhar Chauhan
"""

from pathlib import Path
import cv2

# ==========================================================
# Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET = PROJECT_ROOT / "dataset"

SETS = ["train", "valid", "test"]

# ==========================================================

total_images = 0
total_labels = 0

missing_labels = []
missing_images = []
corrupted_images = []
invalid_labels = []
empty_labels = []

# ==========================================================

for dataset in SETS:

    image_dir = DATASET / dataset / "images"
    label_dir = DATASET / dataset / "labels"

    print("\n" + "=" * 60)
    print(dataset.upper())
    print("=" * 60)

    images = list(image_dir.glob("*"))

    labels = list(label_dir.glob("*.txt"))

    print(f"Images : {len(images)}")
    print(f"Labels : {len(labels)}")

    total_images += len(images)
    total_labels += len(labels)

    # -----------------------------------------
    # Check Images
    # -----------------------------------------

    for image in images:

        label = label_dir / (image.stem + ".txt")

        if not label.exists():
            missing_labels.append(image)

        img = cv2.imread(str(image))

        if img is None:
            corrupted_images.append(image)

    # -----------------------------------------
    # Check Labels
    # -----------------------------------------

    for label in labels:

        image_found = False

        for ext in [".jpg", ".jpeg", ".png"]:

            img = image_dir / (label.stem + ext)

            if img.exists():
                image_found = True
                break

        if not image_found:
            missing_images.append(label)

        with open(label) as f:

            lines = f.readlines()

        if len(lines) == 0:

            empty_labels.append(label)

            continue

        for line in lines:

            parts = line.strip().split()

            if len(parts) != 5:

                invalid_labels.append(label)

                continue

            cls = int(float(parts[0]))

            x = float(parts[1])
            y = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])

            if not (
                0 <= x <= 1
                and 0 <= y <= 1
                and 0 <= w <= 1
                and 0 <= h <= 1
            ):

                invalid_labels.append(label)

# ==========================================================

print("\n")
print("=" * 70)
print("DATASET SUMMARY")
print("=" * 70)

print(f"Total Images : {total_images}")
print(f"Total Labels : {total_labels}")

print()

print(f"Missing Labels    : {len(missing_labels)}")
print(f"Missing Images    : {len(missing_images)}")
print(f"Corrupted Images  : {len(corrupted_images)}")
print(f"Empty Labels      : {len(empty_labels)}")
print(f"Invalid Labels    : {len(invalid_labels)}")

print()

if (
    len(missing_labels)
    + len(missing_images)
    + len(corrupted_images)
    + len(empty_labels)
    + len(invalid_labels)
) == 0:

    print("✅ Dataset Verified Successfully!")

else:

    print("⚠ Dataset has issues.")

print("=" * 70)