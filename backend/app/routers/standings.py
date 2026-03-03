from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analytics

router = APIRouter(prefix="/api", tags=["standings"])


@router.get("/standings/drivers")
def driver_standings(season: int, db: Session = Depends(get_db)):
    return analytics.get_driver_standings(db, season)


@router.get("/standings/constructors")
def constructor_standings(season: int, db: Session = Depends(get_db)):
    return analytics.get_constructor_standings(db, season)
