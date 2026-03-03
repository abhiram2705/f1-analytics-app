from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.race import Race, Season
from app.schemas.race import RaceOut, SeasonOut
from app.services import analytics

router = APIRouter(prefix="/api", tags=["races"])


@router.get("/seasons", response_model=List[SeasonOut])
def list_seasons(db: Session = Depends(get_db)):
    return db.query(Season).order_by(Season.year.desc()).all()


@router.get("/races", response_model=List[RaceOut])
def list_races(season: int, db: Session = Depends(get_db)):
    return (
        db.query(Race)
        .filter(Race.season == season)
        .order_by(Race.round)
        .all()
    )


@router.get("/races/{race_id}", response_model=RaceOut)
def get_race(race_id: int, db: Session = Depends(get_db)):
    race = db.get(Race, race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race


@router.get("/races/{race_id}/results")
def get_race_results(race_id: int, db: Session = Depends(get_db)):
    return analytics.get_race_results(db, race_id)
