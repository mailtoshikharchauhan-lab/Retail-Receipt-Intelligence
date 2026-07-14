"""
analytics.py

Analytics API Routes

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database.database import get_db
from api.database import crud

from api.schemas import AnalyticsResponse

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ==========================================================
# Dashboard Analytics
# ==========================================================

@router.get(
    "/",
    response_model=AnalyticsResponse
)
def get_dashboard_analytics(
    db: Session = Depends(get_db)
):
    """
    Returns dashboard analytics.
    """

    analytics = crud.get_analytics(db)

    return AnalyticsResponse(**analytics)