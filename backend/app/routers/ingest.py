from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ingestion import ingest_race

router = APIRouter(prefix="/api", tags=["ingest"])


@router.post("/ingest")
def trigger_ingest(season: int, round: int, db: Session = Depends(get_db)):
    """
    Download and store F1 session data for a given season/round.
    FastF1 fetches from the official F1 timing data (cached locally).
    """
    try:
        result = ingest_race(db, season, round)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
