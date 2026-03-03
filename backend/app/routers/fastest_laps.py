from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.services import analytics

router = APIRouter(prefix="/api", tags=["fastest-laps"])


@router.get("/races/{race_id}/fastest-laps")
def fastest_laps(race_id: int, db: Session = Depends(get_db)):
    return analytics.get_fastest_laps(db, race_id)


@router.get("/races/{race_id}/lap-times")
def lap_times(race_id: int, driver_id: Optional[str] = None, db: Session = Depends(get_db)):
    return analytics.get_lap_times(db, race_id, driver_id)


@router.get("/races/{race_id}/race-pace")
def race_pace(race_id: int, window: int = 3, db: Session = Depends(get_db)):
    return analytics.get_race_pace(db, race_id, window)
