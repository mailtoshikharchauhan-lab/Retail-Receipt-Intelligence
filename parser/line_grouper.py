"""
line_grouper.py

Groups EasyOCR bounding boxes into text lines.

Author:
Shikhar Chauhan
"""

from statistics import median


class LineGrouper:

    def __init__(self, y_threshold=None, min_confidence=0.35, threshold_factor=0.55):
        """
        y_threshold : fixed pixel threshold. Leave as None to auto-derive
                       it from this image's own text height -- a fixed
                       number doesn't scale across different resolutions
                       / upscale factors and causes separate rows (e.g.
                       "SUBTOTAL" and the next "SUBTOTAL") to merge.
        threshold_factor : used only when auto-deriving. Fraction of the
                       median box height treated as "same row".
        """
        self.y_threshold = y_threshold
        self.min_confidence = min_confidence
        self.threshold_factor = threshold_factor

    def _center(self, box):
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]

        return (
            sum(xs) / 4,
            sum(ys) / 4
        )

    def _height(self, box):
        ys = [p[1] for p in box]
        return max(ys) - min(ys)

    def group(self, ocr_results):

        words = []

        for item in ocr_results:

            if item["confidence"] < self.min_confidence:
                continue

            cx, cy = self._center(item["box"])

            words.append({
                "text": item["text"],
                "box": item["box"],
                "confidence": item["confidence"],
                "cx": cx,
                "cy": cy,
                "height": self._height(item["box"])
            })

        if not words:
            return []

        # Auto-derive the row threshold from this image's own text
        # height instead of using a fixed pixel constant.
        if self.y_threshold is not None:
            threshold = self.y_threshold
        else:
            median_height = median(w["height"] for w in words)
            threshold = max(median_height * self.threshold_factor, 6)

        words.sort(key=lambda x: x["cy"])

        rows = []

        for word in words:

            added = False

            for row in rows:

                row_y = median([w["cy"] for w in row])

                if abs(word["cy"] - row_y) < threshold:

                    row.append(word)

                    added = True

                    break

            if not added:

                rows.append([word])

        output = []

        for row in rows:

            row.sort(key=lambda x: x["cx"])

            text = " ".join([w["text"] for w in row])

            output.append({
                "text": text,
                "words": row
            })

        return output