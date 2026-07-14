"""
crop_receipt.py

Crop detected receipt using YOLO.

Author:
Shikhar Chauhan
"""

from pathlib import Path
import cv2


def crop_receipt(result, image_path, output_dir):
    """
    Crop highest-confidence receipt.

    Args:
        result : YOLO Result
        image_path : Original image path
        output_dir : Output folder

    Returns:
        Cropped image path
    """

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not read image: {image_path}")
        return None

    if len(result.boxes) == 0:
        print(f"No receipt detected in {image_path.name}")
        return None

    # Highest confidence detection
    box = result.boxes[0]

    x1, y1, x2, y2 = map(int, box.xyxy[0])

    # Prevent negative coordinates
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(image.shape[1], x2)
    y2 = min(image.shape[0], y2)

    crop = image[y1:y2, x1:x2]

    output_dir.mkdir(parents=True, exist_ok=True)

    save_path = output_dir / image_path.name

    cv2.imwrite(str(save_path), crop)

    print(f"Cropped -> {save_path.name}")

    return save_path