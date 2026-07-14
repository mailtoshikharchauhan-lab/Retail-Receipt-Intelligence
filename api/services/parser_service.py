"""
parser_service.py

Receipt Parser Service

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

import logging

from parser.parser import ReceiptParser


logger = logging.getLogger(__name__)


class ParserService:
    """
    Wrapper around ReceiptParser.

    Responsibilities:
        - Parse OCR output
        - Return structured receipt
    """

    def __init__(self):

        logger.info("Initializing Receipt Parser...")

        self.parser = ReceiptParser()

        logger.info("Receipt Parser initialized.")

    # ---------------------------------------------------------

    def parse(
        self,
        ocr_result
    ) -> dict:
        """
        Parse OCR output.

        Parameters
        ----------
        ocr_result

        Returns
        -------
        dict
            Parsed receipt.
        """

        logger.info("Parsing receipt...")

        receipt = self.parser.parse(ocr_result)

        logger.info("Receipt parsed successfully.")

        return receipt

    # ---------------------------------------------------------

    def process(
        self,
        ocr_result
    ) -> dict:
        """
        Complete parser pipeline.

        OCR Result

            ↓

        Receipt Parser

            ↓

        Structured Receipt
        """

        return self.parse(ocr_result)