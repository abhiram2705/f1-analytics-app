"""
Pre-computed analytics queries used by the routers.
All functions accept a SQLAlchemy Session and return plain dicts/lists.
"""
from typing import List, Optional
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.lap import Lap
from app.models.driver import Driver
from app.models.race import Constructor


def get_fastest_laps(db: Session, race_id: int) -> List[dict]:
    """Return the single fastest lap per driver for a given race."""
    rows = db.execute(text("""
        SELECT
            d.driver_id,
            d.code AS driver_code,
            d.full_name AS driver_name,
            d.team_id,
            c.name AS team_name,
            l.lap_number,
            l.lap_time_ms,
            l.s1_ms,
            l.s2_ms,
            l.s3_ms,
            l.compound
        FROM laps l
        JOIN drivers d ON d.driver_id = l.driver_id
        LEFT JOIN constructors c ON c.team_id = d.team_id
        WHERE l.race_id = :race_id
          AND l.lap_time_ms IS NOT NULL
          AND l.lap_time_ms = (
              SELECT MIN(l2.lap_time_ms)
              FROM laps l2
              WHERE l2.race_id = l.race_id
                AND l2.driver_id = l.driver_id
                AND l2.lap_time_ms IS NOT NULL
          )
        ORDER BY l.lap_time_ms
    """), {"race_id": race_id}).mappings().all()
    return [dict(r) for r in rows]


def get_tyre_degradation(db: Session, race_id: int) -> List[dict]:
    """Average lap time by compound + tyre life age, excluding safety car laps."""
    rows = db.execute(text("""
        SELECT
            l.compound,
            l.tyre_life,
            AVG(l.lap_time_ms) AS avg_lap_time_ms,
            COUNT(*) AS sample_count
        FROM laps l
        WHERE l.race_id = :race_id
          AND l.lap_time_ms IS NOT NULL
          AND l.compound IS NOT NULL
          AND l.tyre_life IS NOT NULL
          AND (l.track_status = '1' OR l.track_status IS NULL)
        GROUP BY l.compound, l.tyre_life
        ORDER BY l.compound, l.tyre_life
    """), {"race_id": race_id}).mappings().all()
    return [dict(r) for r in rows]


def get_pit_stops(db: Session, race_id: int) -> List[dict]:
    rows = db.execute(text("""
        SELECT
            p.pit_id,
            p.race_id,
            p.driver_id,
            d.code AS driver_code,
            d.full_name AS driver_name,
            d.team_id,
            c.name AS team_name,
            p.stop_number,
            p.lap,
            p.duration_ms
        FROM pit_stops p
        JOIN drivers d ON d.driver_id = p.driver_id
        LEFT JOIN constructors c ON c.team_id = d.team_id
        WHERE p.race_id = :race_id
        ORDER BY p.lap, p.driver_id
    """), {"race_id": race_id}).mappings().all()
    return [dict(r) for r in rows]


def get_stints(db: Session, race_id: int) -> List[dict]:
    rows = db.execute(text("""
        SELECT
            s.stint_id,
            s.race_id,
            s.driver_id,
            d.code AS driver_code,
            d.full_name AS driver_name,
            d.team_id,
            c.name AS team_name,
            s.stint_number,
            s.compound,
            s.start_lap,
            s.end_lap,
            (s.end_lap - s.start_lap + 1) AS length
        FROM stints s
        JOIN drivers d ON d.driver_id = s.driver_id
        LEFT JOIN constructors c ON c.team_id = d.team_id
        WHERE s.race_id = :race_id
        ORDER BY s.driver_id, s.stint_number
    """), {"race_id": race_id}).mappings().all()
    return [dict(r) for r in rows]


def get_race_pace(db: Session, race_id: int, window: int = 3) -> List[dict]:
    """Rolling average lap time (window laps) per driver, excluding outliers."""
    rows = db.execute(text("""
        SELECT
            l.driver_id,
            d.code AS driver_code,
            d.team_id,
            l.lap_number,
            l.lap_time_ms
        FROM laps l
        JOIN drivers d ON d.driver_id = l.driver_id
        WHERE l.race_id = :race_id
          AND l.lap_time_ms IS NOT NULL
          AND (l.track_status = '1' OR l.track_status IS NULL)
        ORDER BY l.driver_id, l.lap_number
    """), {"race_id": race_id}).mappings().all()

    # Compute rolling average in Python
    df = pd.DataFrame([dict(r) for r in rows])
    if df.empty:
        return []

    result = []
    for driver_id, grp in df.groupby("driver_id"):
        grp = grp.sort_values("lap_number").copy()
        grp["rolling_avg_ms"] = grp["lap_time_ms"].rolling(window, min_periods=1).mean()
        for _, row in grp.iterrows():
            result.append({
                "driver_id": row["driver_id"],
                "driver_code": row["driver_code"],
                "team_id": row["team_id"],
                "lap_number": int(row["lap_number"]),
                "rolling_avg_ms": round(row["rolling_avg_ms"], 2),
            })
    return result


def get_lap_times(db: Session, race_id: int, driver_id: Optional[str] = None) -> List[dict]:
    query = """
        SELECT l.lap_id, l.race_id, l.driver_id, l.lap_number,
               l.lap_time_ms, l.s1_ms, l.s2_ms, l.s3_ms,
               l.compound, l.tyre_life, l.is_personal_best, l.track_status
        FROM laps l
        WHERE l.race_id = :race_id
    """
    params: dict = {"race_id": race_id}
    if driver_id:
        query += " AND l.driver_id = :driver_id"
        params["driver_id"] = driver_id
    query += " ORDER BY l.driver_id, l.lap_number"
    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


def get_race_results(db: Session, race_id: int) -> List[dict]:
    rows = db.execute(text("""
        SELECT
            rr.driver_id,
            d.code AS driver_code,
            d.full_name AS driver_name,
            d.team_id,
            c.name AS team_name,
            rr.position,
            rr.grid,
            rr.points,
            rr.status,
            rr.fastest_lap_rank,
            rr.fastest_lap_time_ms
        FROM race_results rr
        JOIN drivers d ON d.driver_id = rr.driver_id
        LEFT JOIN constructors c ON c.team_id = d.team_id
        WHERE rr.race_id = :race_id
        ORDER BY rr.position
    """), {"race_id": race_id}).mappings().all()
    return [dict(r) for r in rows]


def get_driver_standings(db: Session, season: int) -> List[dict]:
    rows = db.execute(text("""
        SELECT
            ds.round,
            ds.driver_id,
            d.code AS driver_code,
            d.full_name AS driver_name,
            d.team_id,
            ds.position,
            ds.points,
            ds.wins
        FROM driver_standings ds
        JOIN drivers d ON d.driver_id = ds.driver_id
        WHERE ds.season = :season
        ORDER BY ds.round, ds.position
    """), {"season": season}).mappings().all()
    return [dict(r) for r in rows]


def get_constructor_standings(db: Session, season: int) -> List[dict]:
    rows = db.execute(text("""
        SELECT
            cs.round,
            cs.team_id,
            c.name AS team_name,
            cs.position,
            cs.points,
            cs.wins
        FROM constructor_standings cs
        JOIN constructors c ON c.team_id = cs.team_id
        WHERE cs.season = :season
        ORDER BY cs.round, cs.position
    """), {"season": season}).mappings().all()
    return [dict(r) for r in rows]
