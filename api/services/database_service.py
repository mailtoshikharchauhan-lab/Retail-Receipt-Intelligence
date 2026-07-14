"""
database_service.py

Database Service

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

import logging

from sqlalchemy.orm import Session

from api.database import crud


logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Wrapper around CRUD operations.

    Keeps ReceiptService independent
    from SQLAlchemy implementation.
    """

    def __init__(
        self,
        db: Session
    ):

        self.db = db

    # ---------------------------------------------------------

    def save_receipt(
        self,
        receipt: dict
    ):
        """
        Save receipt to SQLite.
        """

        logger.info("Saving receipt to database...")

        result = crud.create_receipt(

            self.db,

            receipt

        )

        logger.info("Receipt saved.")

        return result

    # ---------------------------------------------------------

    def get_receipt(
        self,
        receipt_id: int
    ):

        return crud.get_receipt(

            self.db,

            receipt_id

        )

    # ---------------------------------------------------------

    def get_all_receipts(self):

        return crud.get_all_receipts(

            self.db

        )

    # ---------------------------------------------------------

    def delete_receipt(
        self,
        receipt_id: int
    ):

        return crud.delete_receipt(

            self.db,

            receipt_id

        )

    # ---------------------------------------------------------

    def update_status(
        self,
        receipt_id: int,
        status: str
    ):

        return crud.update_receipt_status(

            self.db,

            receipt_id,

            status

        )

    # ---------------------------------------------------------

    def analytics(self):

        return crud.get_analytics(

            self.db

        )