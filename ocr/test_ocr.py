"""
test_ocr.py

Test the complete OCR + Parser pipeline.

Author:
Shikhar Chauhan
"""

import sys
from pathlib import Path

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# ==========================================================
# Imports
# ==========================================================

from ocr.ocr_engine import read_receipt
from parser.parser import ReceiptParser
from utils.save_json import save_json

# ==========================================================
# Image Path
# ==========================================================

IMAGE = PROJECT_ROOT / "outputs" / "crops" / "44.jpg"

if not IMAGE.exists():
    raise FileNotFoundError(
        f"Image not found:\n{IMAGE}"
    )

# ==========================================================
# Run OCR
# ==========================================================

print("=" * 60)
print("Retail Receipt Intelligence")
print("=" * 60)

print(f"Image : {IMAGE.name}")

print("\nRunning EasyOCR...\n")

ocr_result = read_receipt(IMAGE, preprocess_mode='faded')

# ==========================================================
# Parse Receipt
# ==========================================================

parser = ReceiptParser()

receipt = parser.parse(ocr_result)

# ==========================================================
# Save JSON
# ==========================================================

json_name = IMAGE.stem + ".json"

json_path = save_json(
    receipt,
    json_name
)

# ==========================================================
# Display Results
# ==========================================================

print("=" * 60)
print("EXTRACTED RECEIPT INFORMATION")
print("=" * 60)

print(f"Store           : {receipt['store']}")
print(f"Date            : {receipt['date']}")
print(f"Time            : {receipt['time']}")
print(f"Subtotal        : {receipt['subtotal']}")
print(f"Tax             : {receipt['tax']}")
print(f"Total           : {receipt['total']}")
print(f"Payment Method  : {receipt['payment_method']}")

print("\nDetected Items")
print("-" * 60)

if receipt["items"]:

    for idx, item in enumerate(receipt["items"], start=1):

        print(f"{idx}. {item['name']}  --->  {item['price']}")

else:

    print("No items detected.")

print("\nRaw OCR Text")
print("-" * 60)

for line in receipt["raw_text"]:
    print(line)

print("\n" + "=" * 60)
print("JSON Saved Successfully")
print("=" * 60)

print(json_path)