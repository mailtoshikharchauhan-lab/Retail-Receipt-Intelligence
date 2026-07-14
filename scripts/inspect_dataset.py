"""
inspect_dataset.py

Purpose:
--------
Inspect the CVAT OCR Receipt Dataset before converting it to YOLO format.

Outputs:
---------
1. Total images
2. Total annotations
3. Class distribution
4. Image size statistics
5. Missing images
6. Dataset summary

Author:
Shikhar Chauhan
"""

import os
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import cv2

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "dataset" / "raw"

XML_FILE = DATASET_PATH / "annotations.xml"

IMAGE_FOLDER = DATASET_PATH / "images"

# --------------------------------------------------
# Check dataset
# --------------------------------------------------

if not XML_FILE.exists():
    raise FileNotFoundError(f"XML file not found:\n{XML_FILE}")

if not IMAGE_FOLDER.exists():
    raise FileNotFoundError(f"Images folder not found:\n{IMAGE_FOLDER}")

# --------------------------------------------------
# Parse XML
# --------------------------------------------------

print("=" * 60)
print("Reading XML...")
print("=" * 60)

tree = ET.parse(XML_FILE)
root = tree.getroot()

images = root.findall("image")

print(f"Total XML Image Entries : {len(images)}")

# --------------------------------------------------
# Statistics
# --------------------------------------------------

class_counter = Counter()

missing_images = []

total_boxes = 0

image_widths = []

image_heights = []

# --------------------------------------------------
# Loop through images
# --------------------------------------------------

for image in images:

    image_name = image.attrib["name"]

    image_width = int(image.attrib["width"])

    image_height = int(image.attrib["height"])

    image_widths.append(image_width)

    image_heights.append(image_height)

    image_path = IMAGE_FOLDER / Path(image_name).name

    if not image_path.exists():
        missing_images.append(Path(image_name).name)

    # Count Boxes

    for box in image.findall("box"):

        label = box.attrib["label"]

        class_counter[label] += 1

        total_boxes += 1

# --------------------------------------------------
# Image Folder
# --------------------------------------------------

all_images = []

for ext in ["*.jpg", "*.jpeg", "*.png"]:

    all_images.extend(IMAGE_FOLDER.glob(ext))

# --------------------------------------------------
# Report
# --------------------------------------------------

print()

print("=" * 60)
print("DATASET REPORT")
print("=" * 60)

print(f"Images in Folder      : {len(all_images)}")

print(f"Images in XML         : {len(images)}")

print(f"Bounding Boxes        : {total_boxes}")

print()

print("=" * 60)
print("IMAGE SIZE")
print("=" * 60)

print(f"Minimum Width         : {min(image_widths)}")

print(f"Maximum Width         : {max(image_widths)}")

print(f"Minimum Height        : {min(image_heights)}")

print(f"Maximum Height        : {max(image_heights)}")

print()

print("=" * 60)
print("CLASS DISTRIBUTION")
print("=" * 60)

for label, count in class_counter.items():

    print(f"{label:<15} : {count}")

print()

print("=" * 60)
print("MISSING IMAGES")
print("=" * 60)

if len(missing_images) == 0:

    print("No Missing Images")

else:

    print(f"Missing Images : {len(missing_images)}")

    for img in missing_images:

        print(img)

print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)

print("Dataset Inspection Completed Successfully")

print("=" * 60)