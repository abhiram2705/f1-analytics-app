from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analytics

router = APIRouter(prefix="/api", tags=["pit-stops"])


@router.get("/races/{race_id}/pit-stops")
def pit_stops(race_id: int, db: Session = Depends(get_db)):
    return analytics.get_pit_stops(db, race_id)
