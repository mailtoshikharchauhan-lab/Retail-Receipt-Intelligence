"""
parser.py

Extract structured information from OCR text.

Author:
Shikhar Chauhan
"""

import re


def parse_receipt(ocr_results):
    """
    Extract useful fields from OCR output.
    """

    lines = []

    for item in ocr_results:

        text = item["text"].strip()

        if len(text):

            lines.append(text)

    #########################################################

    store = ""

    date = ""

    time = ""

    total = ""

    subtotal = ""

    #########################################################

    items = []

    #########################################################

    date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"

    time_pattern = r"\d{1,2}[:;]\d{2}"

    money_pattern = r"\d+\.\d{2}"

    #########################################################

    if len(lines):

        store = lines[0]

    #########################################################

    for line in lines:

        upper = line.upper()

        #############################

        date_match = re.search(
            date_pattern,
            line
        )

        if date_match:

            date = date_match.group()

        #############################

        time_match = re.search(
            time_pattern,
            line
        )

        if time_match:

            time = time_match.group()

        #############################

        if "TOTAL" in upper:

            amount = re.search(
                money_pattern,
                line
            )

            if amount:

                total = amount.group()

        #############################

        elif "SUBTOTAL" in upper:

            amount = re.search(
                money_pattern,
                line
            )

            if amount:

                subtotal = amount.group()

        #############################

        elif re.search(money_pattern, line):

            items.append(line)

    #########################################################

    return {

        "store": store,

        "date": date,

        "time": time,

        "subtotal": subtotal,

        "total": total,

        "items": items,

        "raw_text": lines

    }