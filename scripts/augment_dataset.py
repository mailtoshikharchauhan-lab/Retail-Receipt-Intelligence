"""
augment_dataset.py

Generate an augmented YOLO dataset.

Author:
Shikhar Chauhan
"""

from pathlib import Path
import cv2
import albumentations as A
from tqdm import tqdm

# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = PROJECT_ROOT / "dataset" / "all" / "images"
LABEL_DIR = PROJECT_ROOT / "dataset" / "all" / "labels"

OUTPUT_IMAGE_DIR = PROJECT_ROOT / "dataset" / "generated" / "images"
OUTPUT_LABEL_DIR = PROJECT_ROOT / "dataset" / "generated" / "labels"

OUTPUT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_LABEL_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================

COPIES_PER_IMAGE = 20

# ============================================================

transform = A.Compose(
    [
        A.Rotate(limit=15, p=0.7),
        A.RandomBrightnessContrast(
            brightness_limit=0.25,
            contrast_limit=0.25,
            p=0.6,
        ),
        A.MotionBlur(blur_limit=5, p=0.3),
        A.GaussianBlur(blur_limit=(3, 5), p=0.2),
        A.GaussNoise(p=0.3),
        A.Perspective(scale=(0.03, 0.08), p=0.4),
        A.RandomScale(scale_limit=0.15, p=0.4),
    ],
    bbox_params=A.BboxParams(
        format="yolo",
        label_fields=["class_labels"],
        min_visibility=0.3,
    ),
)

# ============================================================


def read_yolo(txt_path):
    """
    Read YOLO labels safely.
    """

    boxes = []
    labels = []

    with open(txt_path, "r") as f:

        for line_no, line in enumerate(f, start=1):

            line = line.strip()

            if line == "":
                continue

            values = line.split()

            # Skip invalid labels
            if len(values) != 5:
                print("\n" + "=" * 60)
                print("Invalid Label Found")
                print(txt_path.name)
                print(f"Line {line_no}")
                print(line)
                print("=" * 60)
                continue

            try:

                cls = int(float(values[0]))

                x = float(values[1])
                y = float(values[2])
                w = float(values[3])
                h = float(values[4])

            except ValueError:

                print(f"Skipping invalid values in {txt_path.name}")
                continue

            boxes.append([x, y, w, h])
            labels.append(cls)

    return boxes, labels


# ============================================================


def save_yolo(txt_path, boxes, labels):

    with open(txt_path, "w") as f:

        for cls, box in zip(labels, boxes):

            x, y, w, h = box

            f.write(
                f"{cls} "
                f"{x:.6f} "
                f"{y:.6f} "
                f"{w:.6f} "
                f"{h:.6f}\n"
            )


# ============================================================

images = sorted(
    list(IMAGE_DIR.glob("*.jpg"))
    + list(IMAGE_DIR.glob("*.jpeg"))
    + list(IMAGE_DIR.glob("*.png"))
)

print("=" * 60)
print(f"Found {len(images)} images")
print("=" * 60)

counter = 0
skipped = 0

for image_path in tqdm(images):

    label_path = LABEL_DIR / (image_path.stem + ".txt")

    if not label_path.exists():
        skipped += 1
        print(f"Missing Label : {image_path.name}")
        continue

    image = cv2.imread(str(image_path))

    if image is None:
        skipped += 1
        print(f"Cannot read image : {image_path.name}")
        continue

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes, labels = read_yolo(label_path)

    if len(boxes) == 0:
        skipped += 1
        print(f"No valid boxes : {label_path.name}")
        continue

    # Save original image
    cv2.imwrite(
        str(OUTPUT_IMAGE_DIR / f"{counter:05d}.jpg"),
        cv2.cvtColor(image, cv2.COLOR_RGB2BGR),
    )

    save_yolo(
        OUTPUT_LABEL_DIR / f"{counter:05d}.txt",
        boxes,
        labels,
    )

    counter += 1

    # Generate augmentations
    for _ in range(COPIES_PER_IMAGE):

        try:

            transformed = transform(
                image=image,
                bboxes=boxes,
                class_labels=labels,
            )

        except Exception as e:

            print("\nError while augmenting:")
            print(image_path.name)
            print(e)
            skipped += 1
            continue

        aug_img = transformed["image"]
        aug_boxes = transformed["bboxes"]
        aug_labels = transformed["class_labels"]

        if len(aug_boxes) == 0:
            continue

        cv2.imwrite(
            str(OUTPUT_IMAGE_DIR / f"{counter:05d}.jpg"),
            cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR),
        )

        save_yolo(
            OUTPUT_LABEL_DIR / f"{counter:05d}.txt",
            aug_boxes,
            aug_labels,
        )

        counter += 1

print("\n" + "=" * 60)
print("Dataset Generation Finished")
print("=" * 60)
print(f"Generated Images : {counter}")
print(f"Skipped          : {skipped}")
print(f"Images Saved To  : {OUTPUT_IMAGE_DIR}")
print(f"Labels Saved To  : {OUTPUT_LABEL_DIR}")