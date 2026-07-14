"""
cleaner.py

OCR Cleaner

Uses bounding boxes to reconstruct
receipt lines before parsing.

Author:
Shikhar Chauhan
"""

import re

from parser.line_grouper import LineGrouper


class OCRCleaner:

    def __init__(self):

        self.grouper = LineGrouper()

    # -------------------------------------------------------------

    def clean(self, ocr_result):

        rows = self.grouper.group(ocr_result)

        cleaned = []

        for row in rows:

            text = row["text"]

            text = self.normalize(text)

            if len(text) < 2:
                continue

            cleaned.append(text)

        cleaned = self.merge_prices(cleaned)

        cleaned = self.remove_noise(cleaned)

        return cleaned

    # -------------------------------------------------------------

    def normalize(self, text):

        text = text.upper()

        replacements = {

            "*": "",

            "|": "I",

            "O.": "0.",

            "0O": "00",

            ",": ".",

            "—": "-",

            "_": " "

        }

        for old, new in replacements.items():

            text = text.replace(old, new)

        # Root cause #4: Fix split prices with stray spaces, e.g. "13 .96" -> "13.96"
        text = re.sub(r"(\d+)\s+(\.\d{2})", r"\1\2", text)
        
        # NEW FIX: Handle prices with space but no decimal, e.g. "2 78" -> "2.78"
        # Look for pattern: digit(s) + space + exactly 2 digits at word boundary
        text = re.sub(r"(\d+)\s+(\d{2})(?=\s|$)", r"\1.\2", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # -------------------------------------------------------------

    def merge_prices(self, lines):

        """
        Merge split prices.

        Example

        13
        .96

        ->

        13.96
        """

        merged = []

        i = 0

        while i < len(lines):

            current = lines[i]

            # ------------------------

            if (

                i + 1 < len(lines)

                and re.fullmatch(r"\d+", current)

                and re.fullmatch(r"\.\d{2}", lines[i + 1])

            ):

                merged.append(

                    current + lines[i + 1]

                )

                i += 2

                continue

            # ------------------------

            if (

                i + 1 < len(lines)

                and re.search(r"\d+$", current)

                and re.fullmatch(r"\.\d{2}", lines[i + 1])

            ):

                merged.append(

                    current + lines[i + 1]

                )

                i += 2

                continue

            # ------------------------

            merged.append(current)

            i += 1

        return merged

    # -------------------------------------------------------------

    def remove_noise(self, lines):

        cleaned = []

        ignore = [

            "X",

            "#",

            "CD",

            "ID",

            "TR#",

            "TC#",

            "ST#",

            "FIGURES",

            "VALIDATION",

            "APPROVAL",

            "ACCOUNT",

            "SERVICE",

            "COPY"

        ]

        for line in lines:

            if len(line) < 2:
                continue

            skip = False

            for word in ignore:

                if line == word:

                    skip = True

                    break

            if skip:
                continue

            cleaned.append(line)

        return cleaned