"""
merge_dataset.py

Merge train, valid and test into a single dataset.

Author:
Shikhar Chauhan
"""

from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET = PROJECT_ROOT / "dataset"

TRAIN = DATASET / "train"
VALID = DATASET / "valid"
TEST = DATASET / "test"

OUTPUT_IMAGES = DATASET / "all" / "images"
OUTPUT_LABELS = DATASET / "all" / "labels"

OUTPUT_IMAGES.mkdir(parents=True, exist_ok=True)
OUTPUT_LABELS.mkdir(parents=True, exist_ok=True)


def copy_folder(folder):

    image_folder = folder / "images"
    label_folder = folder / "labels"

    images = list(image_folder.glob("*"))

    print(f"\nCopying {folder.name}")

    for image in images:

        label = label_folder / f"{image.stem}.txt"

        shutil.copy2(
            image,
            OUTPUT_IMAGES / image.name
        )

        shutil.copy2(
            label,
            OUTPUT_LABELS / label.name
        )


copy_folder(TRAIN)
copy_folder(VALID)
copy_folder(TEST)

print("\n====================================")
print("Merge Completed")
print("====================================")

print(f"Images : {len(list(OUTPUT_IMAGES.glob('*')))}")
print(f"Labels : {len(list(OUTPUT_LABELS.glob('*')))}")