"""
visualize_labels.py

Visualize YOLO labels.

Author:
Shikhar Chauhan
"""

from pathlib import Path
import cv2
import random

# --------------------------------------------------------
# Paths
# --------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_FOLDER = PROJECT_ROOT / "dataset" / "raw" / "images"

LABEL_FOLDER = PROJECT_ROOT / "dataset" / "labels"

OUTPUT_FOLDER = PROJECT_ROOT / "outputs"

OUTPUT_FOLDER.mkdir(exist_ok=True)

# --------------------------------------------------------
# Classes
# --------------------------------------------------------

CLASS_NAMES = {
    0: "receipt",
    1: "shop",
    2: "item",
    3: "date_time",
    4: "total"
}

# Random color for each class
COLORS = {}

for cls in CLASS_NAMES:
    COLORS[cls] = (
        random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255)
    )

# --------------------------------------------------------
# Images
# --------------------------------------------------------

images = sorted(IMAGE_FOLDER.glob("*.jpg"))

print(f"Found {len(images)} images")

# --------------------------------------------------------
# Visualize first 20 images
# --------------------------------------------------------

for image_path in images[:20]:

    image = cv2.imread(str(image_path))

    h, w = image.shape[:2]

    label_path = LABEL_FOLDER / f"{image_path.stem}.txt"

    if not label_path.exists():
        print(f"Missing label: {label_path.name}")
        continue

    with open(label_path) as f:

        lines = f.readlines()

    for line in lines:

        cls, xc, yc, bw, bh = map(float, line.split())

        cls = int(cls)

        xc *= w
        yc *= h

        bw *= w
        bh *= h

        xmin = int(xc - bw/2)
        ymin = int(yc - bh/2)

        xmax = int(xc + bw/2)
        ymax = int(yc + bh/2)

        color = COLORS[cls]

        cv2.rectangle(
            image,
            (xmin,ymin),
            (xmax,ymax),
            color,
            2
        )

        cv2.putText(
            image,
            CLASS_NAMES[cls],
            (xmin,max(25,ymin-5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    save_path = OUTPUT_FOLDER / image_path.name

    cv2.imwrite(str(save_path), image)

print()

print("="*60)
print("Visualization Completed")
print("="*60)

print(f"Saved images to:\n{OUTPUT_FOLDER}")