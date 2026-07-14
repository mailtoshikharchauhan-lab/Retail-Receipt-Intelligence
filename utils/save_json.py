"""
save_json.py
"""

import json
from pathlib import Path


def save_json(data, filename):

    output = Path("outputs/json")

    output.mkdir(
        parents=True,
        exist_ok=True
    )

    path = output / filename

    with open(path, "w") as f:

        json.dump(
            data,
            f,
            indent=4
        )

    return path