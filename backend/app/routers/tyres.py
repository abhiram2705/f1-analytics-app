from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analytics

router = APIRouter(prefix="/api", tags=["tyres"])


@router.get("/races/{race_id}/tyre-degradation")
def tyre_degradation(race_id: int, db: Session = Depends(get_db)):
    return analytics.get_tyre_degradation(db, race_id)


@router.get("/races/{race_id}/stints")
def stints(race_id: int, db: Session = Depends(get_db)):
    return analytics.get_stints(db, race_id)
