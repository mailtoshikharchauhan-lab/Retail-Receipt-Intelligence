"""
matcher.py

Store name matching.

Author:
Shikhar Chauhan
"""

from rapidfuzz import process


KNOWN_STORES = [

    "WALMART",

    "TARGET",

    "COSTCO",

    "AMAZON",

    "TRADER JOE'S",

    "SPAR",

    "TESCO",

    "ALDI",

    "LIDL",

    "CARREFOUR"

]


def match_store(text):

    match = process.extractOne(

        text,

        KNOWN_STORES

    )

    if match:

        store, score, _ = match

        if score > 70:

            return store

    return text