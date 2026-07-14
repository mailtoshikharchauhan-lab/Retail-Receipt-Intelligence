"""
split_dataset.py

Split generated dataset into
Train / Validation / Test

Author:
Shikhar Chauhan
"""

from pathlib import Path
import shutil
import random

# ==========================================================
# Configuration
# ==========================================================

RANDOM_SEED = 42

TRAIN_RATIO = 0.80
VALID_RATIO = 0.10
TEST_RATIO = 0.10

# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET = PROJECT_ROOT / "dataset"

IMAGE_DIR = DATASET / "generated" / "images"
LABEL_DIR = DATASET / "generated" / "labels"

TRAIN_IMG = DATASET / "train" / "images"
TRAIN_LBL = DATASET / "train" / "labels"

VALID_IMG = DATASET / "valid" / "images"
VALID_LBL = DATASET / "valid" / "labels"

TEST_IMG = DATASET / "test" / "images"
TEST_LBL = DATASET / "test" / "labels"

# ==========================================================
# Delete old folders
# ==========================================================

folders = [
    TRAIN_IMG,
    TRAIN_LBL,
    VALID_IMG,
    VALID_LBL,
    TEST_IMG,
    TEST_LBL,
]

for folder in folders:

    if folder.exists():
        shutil.rmtree(folder)

    folder.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Read Images
# ==========================================================

images = []

for ext in ["*.jpg", "*.jpeg", "*.png"]:

    images.extend(IMAGE_DIR.glob(ext))

images = sorted(images)

print("=" * 60)
print(f"Total Images Found : {len(images)}")
print("=" * 60)

# ==========================================================
# Shuffle
# ==========================================================

random.seed(RANDOM_SEED)
random.shuffle(images)

# ==========================================================
# Split
# ==========================================================

total = len(images)

train_end = int(total * TRAIN_RATIO)
valid_end = train_end + int(total * VALID_RATIO)

train_images = images[:train_end]
valid_images = images[train_end:valid_end]
test_images = images[valid_end:]

# ==========================================================
# Copy Function
# ==========================================================


def copy_files(image_list, img_dst, lbl_dst):

    copied = 0

    for image in image_list:

        label = LABEL_DIR / (image.stem + ".txt")

        if not label.exists():
            print(f"Missing Label : {image.name}")
            continue

        shutil.copy2(image, img_dst / image.name)
        shutil.copy2(label, lbl_dst / label.name)

        copied += 1

    return copied


# ==========================================================
# Copy
# ==========================================================

train_count = copy_files(train_images, TRAIN_IMG, TRAIN_LBL)
valid_count = copy_files(valid_images, VALID_IMG, VALID_LBL)
test_count = copy_files(test_images, TEST_IMG, TEST_LBL)

# ==========================================================
# Summary
# ==========================================================

print("\n" + "=" * 60)
print("Dataset Split Completed")
print("=" * 60)

print(f"Train Images : {train_count}")
print(f"Valid Images : {valid_count}")
print(f"Test Images  : {test_count}")

print("\nTotal Images :", train_count + valid_count + test_count)

print("\nDataset Ready For YOLO Training")