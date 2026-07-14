"""
parser.py

Smart Receipt Parser

Author:
Shikhar Chauhan
"""

import re

from rapidfuzz import fuzz

from parser.cleaner import OCRCleaner
from parser.matcher import match_store, KNOWN_STORES


class ReceiptParser:

    def __init__(self):

        self.cleaner = OCRCleaner()

        self.reset()

    # -------------------------------------------------------------

    def reset(self):

        self.data = {

            "store": "",

            "date": "",

            "time": "",

            "subtotal": "",

            "tax": "",

            "total": "",

            "payment_method": "",

            "items": [],

            "raw_text": []

        }

    # -------------------------------------------------------------

    def parse(self, ocr_result):

        self.reset()

        # Root cause #15: Graceful degradation for empty OCR results
        if not ocr_result:
            return self.data

        lines = self.cleaner.clean(ocr_result)

        # Root cause #15: Graceful degradation for zero lines after cleaning
        if not lines:
            return self.data

        self.data["raw_text"] = lines

        self.extract_store(lines)

        self.extract_datetime(lines)

        self.extract_totals(lines)

        self.extract_payment(lines)

        self.extract_items(lines)

        self.reconcile_totals()

        return self.data

    # -------------------------------------------------------------

    def extract_store(self, lines):

        if not lines:
            return

        best_match = ""
        best_score = 0

        # Check the first several lines (store name/logo is always
        # near the top) rather than assuming line 0 -- promotional
        # text ("See back of receipt for...") sometimes prints above
        # the logo and would otherwise get returned as the store name.
        for line in lines[:6]:

            match = match_store(line)

            score = fuzz.partial_ratio(match, line)

            if match in KNOWN_STORES and score > best_score:
                best_match = match
                best_score = score

        self.data["store"] = best_match or match_store(lines[0])

    # -------------------------------------------------------------

    def extract_datetime(self, lines):

        date_patterns = [

            r"\d{2}/\d{2}/\d{2,4}",

            r"\d{2}-\d{2}-\d{2,4}",

            r"\d{4}-\d{2}-\d{2}",

            r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{1,2}"

        ]

        time_pattern = r"\d{1,2}:\d{2}(:\d{2})?"

        for line in lines:

            if not self.data["date"]:

                for pattern in date_patterns:

                    m = re.search(pattern, line)

                    if m:

                        self.data["date"] = m.group()

                        break

            if not self.data["time"]:

                m = re.search(time_pattern, line)

                if m:

                    self.data["time"] = m.group()

    # -------------------------------------------------------------

    def extract_totals(self, lines):

        # Match prices with optional spaces around the decimal point
        money = r"\d+\s*\.\s*\d{2}"
        
        # Root cause #13: Multiple tax lines must be summed, not overwritten
        tax_values = []

        for line in lines:

            upper = line.upper()
            
            # Skip lines that are change/payment/transaction metadata, not financial totals
            skip_patterns = ["CHANGE", "DUE", "PURCHASE", "REJECTED", "PAYMENT"]
            if any(pattern in upper for pattern in skip_patterns):
                continue

            values = re.findall(money, line)

            if not values:
                continue

            # Normalize value by removing spaces
            value = values[-1].replace(" ", "")

            # IMPORTANT:
            # Check SUBTOTAL before TOTAL (root cause #3)

            if "SUBTOTAL" in upper:

                self.data["subtotal"] = value

            elif re.search(r"\bTOTAL\b", upper):

                self.data["total"] = value

            # NEW: Handle OCR misreads of "TAX" like "IAX", "1AX", "TAK", etc.
            # Common pattern: [I1T][AH][XK] followed by digits/percent/amount
            elif "TAX" in upper or re.search(r"\b[IT1][AH][XK]\s*\d", upper):

                tax_values.append(float(value))
        
        # Sum all tax lines found
        if tax_values:
            self.data["tax"] = f"{sum(tax_values):.2f}"

    # -------------------------------------------------------------

    def extract_payment(self, lines):

        methods = [

            "VISA",

            "CARD",

            "MASTERCARD",

            "AMEX",

            "DISCOVER",

            "DEBIT",  # Moved up before checking other patterns

            "CREDIT",

            "UPI",

            "PHONEPE",

            "PAYTM",

            "GOOGLE PAY",

            "CASH"

        ]

        for line in lines:

            upper = line.upper()

            for method in methods:

                if method in upper:
                    
                    # NEW: Skip if this is transaction metadata, not payment type
                    # e.g. "DEBIT TEND" or "US DEBIT 5870" (account number)
                    if method == "DEBIT":
                        # Only accept if it's clearly a payment line (with TEND or standalone)
                        if "TEND" in upper or "PAYMENT" in upper or line.strip() == "DEBIT":
                            self.data["payment_method"] = method
                            return
                        # Skip "US DEBIT [digits]" pattern (account info, not payment type)
                        if re.search(r"US DEBIT\s+\d{4}", upper):
                            continue
                    else:
                        self.data["payment_method"] = method
                        return

    # -------------------------------------------------------------

    def extract_items(self, lines):

        ignore = [

            "TOTAL",

            "SUBTOTAL",

            "TAX",
            
            "IAX",  # Common OCR misread of "TAX"
            
            "1AX",  # Common OCR misread of "TAX"

            "CHANGE",

            "PAYMENT",

            "ACCOUNT",

            "APPROVAL",

            "VALIDATION",

            "CUSTOMER",

            "COPY",

            "STORE",

            "MANAGER",

            "THANK",

            "WELCOME",

            "PHONE",

            "TEL",

            "TC#",

            "TR#",

            "ST#",

            "TEND",

            "DEBIT",

            "CREDIT",

            "PURCHASE",

            "EFT",

            "REF #",

            "NETWORK",

            "TERMINAL",

            "AID ",

            "AAC",

            "ITEMS SOLD",

            "DUE",  # NEW: "CHANGE DUE", "AMOUNT DUE"

            "BALANCE",

            "RECORDS",

            "FEEDBACK",

            "SURVEY",
            
            "REJECTED",  # NEW: Payment rejected lines
            
            "VISA",  # NEW: Card type/number lines (unless with TEND)
            
            "MASTERCARD",
            
            "AMEX"

        ]

        # Match prices with optional spaces around the decimal point
        money = r"\d+\s*\.\s*\d{2}"
        
        # NEW: Date/time patterns to exclude from items
        date_pattern = r"\d{2}/\d{2}/\d{2,4}"
        time_pattern = r"\d{1,2}:\d{2}"
        
        # NEW: Pattern to detect UPC codes (long digit sequences)
        upc_pattern = r"\b\d{12,14}\b"

        items = []
        previous_line_info = None  # Track previous line for orphaned prices

        for idx, line in enumerate(lines):

            upper = line.upper()

            # Check ignore list (but be smart about VISA/DEBIT with TEND)
            should_ignore = False
            for word in ignore:
                if word in upper:
                    # Special case: don't ignore if it's a payment line with TEND
                    if word in ["VISA", "MASTERCARD", "AMEX", "DEBIT", "CREDIT"] and "TEND" in upper:
                        continue
                    should_ignore = True
                    break
            
            if should_ignore:
                previous_line_info = None  # Reset tracking
                continue
            
            # NEW: Skip lines that are clearly date/time stamps
            if re.search(date_pattern, line) and re.search(time_pattern, line):
                previous_line_info = None
                continue

            values = re.findall(money, line)

            # Check if this line is ONLY a price (orphaned price - item name missing or on previous line)
            line_stripped = line.strip()
            if re.match(r"^\d+\s*\.\s*\d{2}$", line_stripped):
                # This is an orphaned price line
                price_str = line_stripped.replace(" ", "")
                try:
                    price = float(price_str)
                    if 0.01 <= price <= 9999.99:
                        # Try to get item name from previous line info
                        if previous_line_info and previous_line_info.get('has_upc'):
                            # Previous line had a UPC but maybe the item description continues
                            # Use a generic continuation name
                            base_name = previous_line_info.get('name', 'Item')
                            items.append({
                                "name": f"{base_name} (continued)",
                                "price": price
                            })
                        else:
                            # Create a placeholder item
                            items.append({
                                "name": f"Unknown Item {len(items) + 1}",
                                "price": price
                            })
                except ValueError:
                    pass
                previous_line_info = None
                continue

            if not values:
                # No price on this line - might be item name waiting for price on next line
                # But for Walmart receipts, this is rare. Usually each line has UPC + price
                previous_line_info = None
                continue
            
            # NEW: Find UPC codes in the line
            upc_matches = re.findall(upc_pattern, line)
            
            # NEW: If there's a UPC code that looks like a price (has decimal), remove it from consideration
            # Example: "SHIRT DRESS 019493134824.11 48" - the UPC ends with .11 making it look like a price
            filtered_values = []
            for val in values:
                val_clean = val.replace(" ", "")
                # Check if this "price" is actually part of a UPC
                is_upc_part = False
                for upc in upc_matches:
                    # If the value appears within or adjacent to a UPC, it's likely part of the UPC
                    if upc in line and val in line:
                        # Find positions
                        upc_pos = line.find(upc)
                        val_pos = line.find(val)
                        # If they overlap or are very close, it's likely the same number
                        if abs(upc_pos - val_pos) < len(val):
                            is_upc_part = True
                            break
                
                if not is_upc_part:
                    # Also filter out unrealistic prices (likely UPC misreads)
                    try:
                        price_float = float(val_clean)
                        # Reasonable receipt item price range: $0.01 to $9,999.99
                        if 0.01 <= price_float <= 9999.99:
                            filtered_values.append(val)
                    except ValueError:
                        continue
            
            if not filtered_values:
                previous_line_info = None
                continue
            
            # Take the last valid price
            price_str = filtered_values[-1].replace(" ", "")
            price = float(price_str)

            # Remove all price matches from the line to get the item name
            name = line
            for val in values:
                name = name.replace(val, "", 1)  # Remove only first occurrence
            
            name = name.strip()
            name = re.sub(r"\s+", " ", name)

            if len(name) < 3:
                previous_line_info = None
                continue

            if len(name) > 80:
                previous_line_info = None
                continue
            
            # NEW: Skip lines that are just numbers (card numbers, transaction IDs)
            if re.match(r"^[\d\s]+[A-Z]?$", name):
                previous_line_info = None
                continue

            items.append({

                "name": name,

                "price": price

            })
            
            # Track this line for potential orphaned price on next line
            previous_line_info = {
                'name': name,
                'has_upc': len(upc_matches) > 0,
                'price': price
            }

        self.data["items"] = items

    # -------------------------------------------------------------

    def reconcile_totals(self):
        """
        OCR sometimes fully drops one of subtotal/tax/total (the
        digits are never detected at all, not just misread). When
        two of the three are known, the third is arithmetically
        recoverable. When subtotal is still missing, fall back to
        the sum of detected item prices as a best-effort estimate.

        Anything filled in this way is flagged in
        self.data["reconciled_fields"] so callers know it wasn't
        read directly off the receipt.
        """

        def to_float(value):
            try:
                return round(float(value), 2)
            except (TypeError, ValueError):
                return None

        subtotal = to_float(self.data["subtotal"])
        tax = to_float(self.data["tax"])
        total = to_float(self.data["total"])

        reconciled = []

        if subtotal is not None and tax is not None and total is None:
            self.data["total"] = f"{subtotal + tax:.2f}"
            reconciled.append("total")

        elif subtotal is not None and total is not None and tax is None:
            self.data["tax"] = f"{max(total - subtotal, 0):.2f}"
            reconciled.append("tax")

        elif tax is not None and total is not None and subtotal is None:
            self.data["subtotal"] = f"{max(total - tax, 0):.2f}"
            reconciled.append("subtotal")

        if not self.data["subtotal"] and self.data["items"]:
            item_sum = sum(item["price"] for item in self.data["items"])
            if item_sum > 0:
                self.data["subtotal"] = f"{item_sum:.2f}"
                reconciled.append("subtotal (from items)")

        if reconciled:
            self.data["reconciled_fields"] = reconciled