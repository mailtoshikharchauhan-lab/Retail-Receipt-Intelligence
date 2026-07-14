"""
convert_cvat_to_yolo.py

Converts CVAT XML annotations to YOLO format.

Author:
Shikhar Chauhan
"""

from pathlib import Path
import xml.etree.ElementTree as ET
from tqdm import tqdm

# ----------------------------------------------------
# Project Paths
# ----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATASET = PROJECT_ROOT / "dataset" / "raw"

XML_FILE = RAW_DATASET / "annotations.xml"

OUTPUT_LABELS = PROJECT_ROOT / "dataset" / "labels"

OUTPUT_LABELS.mkdir(exist_ok=True)

# ----------------------------------------------------
# Classes
# ----------------------------------------------------

CLASSES = {
    "receipt": 0,
    "shop": 1,
    "item": 2,
    "date_time": 3,
    "total": 4
}

# ----------------------------------------------------
# Functions
# ----------------------------------------------------


def normalize_box(xmin, ymin, xmax, ymax, width, height):

    x_center = ((xmin + xmax) / 2) / width
    y_center = ((ymin + ymax) / 2) / height

    w = (xmax - xmin) / width
    h = (ymax - ymin) / height

    return x_center, y_center, w, h


def polygon_to_bbox(points):

    coordinates = []

    for point in points.split(";"):

        x, y = point.split(",")

        coordinates.append((float(x), float(y)))

    xs = [p[0] for p in coordinates]
    ys = [p[1] for p in coordinates]

    xmin = min(xs)
    xmax = max(xs)

    ymin = min(ys)
    ymax = max(ys)

    return xmin, ymin, xmax, ymax


# ----------------------------------------------------
# Read XML
# ----------------------------------------------------

print("=" * 60)
print("Loading XML...")
print("=" * 60)

tree = ET.parse(XML_FILE)

root = tree.getroot()

images = root.findall("image")

print(f"Images Found : {len(images)}")

print()

# ----------------------------------------------------
# Convert
# ----------------------------------------------------

for image in tqdm(images):

    image_name = Path(image.attrib["name"]).stem

    width = float(image.attrib["width"])
    height = float(image.attrib["height"])

    label_path = OUTPUT_LABELS / f"{image_name}.txt"

    with open(label_path, "w") as f:

        # -----------------------------
        # Polygon (Receipt)
        # -----------------------------

        for polygon in image.findall("polygon"):

            label = polygon.attrib["label"]

            if label not in CLASSES:
                continue

            xmin, ymin, xmax, ymax = polygon_to_bbox(
                polygon.attrib["points"]
            )

            x, y, w, h = normalize_box(
                xmin,
                ymin,
                xmax,
                ymax,
                width,
                height,
            )

            f.write(
                f"{CLASSES[label]} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n"
            )

        # -----------------------------
        # Boxes
        # -----------------------------

        for box in image.findall("box"):

            label = box.attrib["label"]

            if label not in CLASSES:
                continue

            xmin = float(box.attrib["xtl"])
            ymin = float(box.attrib["ytl"])
            xmax = float(box.attrib["xbr"])
            ymax = float(box.attrib["ybr"])

            x, y, w, h = normalize_box(
                xmin,
                ymin,
                xmax,
                ymax,
                width,
                height,
            )

            f.write(
                f"{CLASSES[label]} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n"
            )

print()

print("=" * 60)
print("Conversion Completed Successfully")
print("=" * 60)

print(f"Labels saved in:\n{OUTPUT_LABELS}")