"""
FastF1 → SQL Server ingestion pipeline.

Usage:
    from app.services.ingestion import ingest_race
    result = ingest_race(db, season=2024, round_number=1)
"""
import os
import math
import logging
from datetime import date
from typing import Optional

import fastf1
import pandas as pd
import httpx
from sqlalchemy.orm import Session

from app.models.race import Season, Circuit, Constructor, Race
from app.models.driver import Driver
from app.models.lap import Lap
from app.models.stint import Stint
from app.models.pit_stop import PitStop
from app.models.result import RaceResult, DriverStanding, ConstructorStanding

logger = logging.getLogger(__name__)

# Enable FastF1 cache
_cache_dir = os.getenv("FF1_CACHE_DIR", "./ff1_cache")
os.makedirs(_cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(_cache_dir)

# Team color map for UI
TEAM_COLORS = {
    "red_bull": "#3671C6",
    "ferrari": "#E8002D",
    "mercedes": "#27F4D2",
    "mclaren": "#FF8000",
    "aston_martin": "#229971",
    "alpine": "#FF87BC",
    "williams": "#64C4FF",
    "rb": "#6692FF",
    "haas": "#B6BABD",
    "kick_sauber": "#52E252",
}


def _safe_float(val) -> Optional[float]:
    """Convert pandas Timedelta / float to milliseconds float, None on NaT/NaN."""
    if val is None:
        return None
    if pd.isna(val):
        return None
    if hasattr(val, "total_seconds"):
        return val.total_seconds() * 1000
    try:
        f = float(val)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def _safe_int(val) -> Optional[int]:
    try:
        if pd.isna(val):
            return None
        return int(val)
    except (TypeError, ValueError):
        return None


def _upsert_season(db: Session, year: int):
    s = db.get(Season, year)
    if not s:
        s = Season(year=year)
        db.add(s)
        db.flush()


def _upsert_circuit(db: Session, circuit_key: str, name: str, country: str, city: str) -> str:
    cid = circuit_key.lower().replace(" ", "_")
    c = db.get(Circuit, cid)
    if not c:
        c = Circuit(circuit_id=cid, name=name, country=country, city=city)
        db.add(c)
        db.flush()
    return cid


def _upsert_constructor(db: Session, team_id: str, name: str) -> str:
    tid = team_id.lower().replace(" ", "_")
    t = db.get(Constructor, tid)
    if not t:
        t = Constructor(team_id=tid, name=name)
        db.add(t)
        db.flush()
    return tid


def _upsert_driver(db: Session, driver_id: str, code: str, full_name: str,
                   number: Optional[int], team_id: str) -> str:
    did = driver_id.lower()
    d = db.get(Driver, did)
    if not d:
        d = Driver(driver_id=did, code=code, full_name=full_name,
                   number=number, team_id=team_id)
        db.add(d)
    else:
        d.team_id = team_id  # update team each race (driver may switch)
    return did


def ingest_race(db: Session, season: int, round_number: int) -> dict:
    """Download FastF1 session data and store in the database."""
    logger.info(f"Ingesting season={season} round={round_number}")

    session = fastf1.get_session(season, round_number, "R")
    session.load(laps=True, telemetry=False, weather=False, messages=False)

    event = session.event
    race_name = event["EventName"]
    race_date = event["EventDate"].date() if hasattr(event["EventDate"], "date") else None
    circuit_name = event.get("Location", race_name)
    country = event.get("Country", "")
    city = event.get("Location", "")

    laps_df = session.laps
    results_df = session.results if hasattr(session, "results") else pd.DataFrame()

    # ---- Season & Circuit ----
    _upsert_season(db, season)
    circuit_id = _upsert_circuit(
        db, str(event.get("CircuitKey", circuit_name)), circuit_name, country, city
    )

    # ---- Race record (wipe old data on re-ingest) ----
    existing_race = (
        db.query(Race).filter(Race.season == season, Race.round == round_number).first()
    )
    if existing_race:
        race_id = existing_race.race_id
        db.query(Lap).filter(Lap.race_id == race_id).delete()
        db.query(Stint).filter(Stint.race_id == race_id).delete()
        db.query(PitStop).filter(PitStop.race_id == race_id).delete()
        db.query(RaceResult).filter(RaceResult.race_id == race_id).delete()
        db.flush()
    else:
        race = Race(season=season, round=round_number, name=race_name,
                    circuit_id=circuit_id, date=race_date)
        db.add(race)
        db.flush()
        race_id = race.race_id

    # ---- Constructors & Drivers ----
    # Source from laps: Driver (3-letter code) and Team (full name) are always populated.
    # Enrich full names from results if available (Abbreviation → FullName).
    full_name_map: dict[str, str] = {}   # "VER" -> "Max Verstappen"
    number_map:    dict[str, int] = {}    # "VER" -> 1

    if not results_df.empty:
        for _, row in results_df.iterrows():
            abbr = str(row.get("Abbreviation", "")).strip()
            if not abbr:
                continue
            fn = str(row.get("FullName", row.get("BroadcastName", abbr))).strip()
            full_name_map[abbr] = fn
            num = _safe_int(row.get("DriverNumber"))
            if num:
                number_map[abbr] = num

    # Build unique (driver_code, team_name) pairs from laps
    driver_team = (
        laps_df[["Driver", "Team"]].drop_duplicates()
        .rename(columns={"Driver": "code", "Team": "team_name"})
    )

    for _, drow in driver_team.iterrows():
        code      = str(drow["code"]).strip()          # e.g. "VER"
        team_name = str(drow["team_name"]).strip()     # e.g. "Red Bull Racing"
        driver_id = code.lower()                        # e.g. "ver"
        team_id   = _upsert_constructor(db, team_name, team_name)
        full_name = full_name_map.get(code, code)
        number    = number_map.get(code)
        _upsert_driver(db, driver_id, code, full_name, number, team_id)

    db.flush()

    # ---- Laps ----
    laps_inserted = 0
    lap_rows = []
    for _, row in laps_df.iterrows():
        driver_id = str(row.get("Driver", "unk")).strip().lower()
        lap_num   = _safe_int(row.get("LapNumber"))
        if not lap_num:
            continue
        lap_rows.append(Lap(
            race_id=race_id,
            driver_id=driver_id,
            lap_number=lap_num,
            lap_time_ms=_safe_float(row.get("LapTime")),
            s1_ms=_safe_float(row.get("Sector1Time")),
            s2_ms=_safe_float(row.get("Sector2Time")),
            s3_ms=_safe_float(row.get("Sector3Time")),
            compound=str(row.get("Compound", "")).strip() or None,
            tyre_life=_safe_int(row.get("TyreLife")),
            is_personal_best=bool(row.get("IsPersonalBest", False)),
            track_status=str(row.get("TrackStatus", "")).strip() or None,
        ))
        laps_inserted += 1
    db.bulk_save_objects(lap_rows)
    db.flush()

    # ---- Stints ----
    stints_inserted = 0
    if "Stint" in laps_df.columns:
        stint_rows = []
        for (drv, stint_num), grp in laps_df.groupby(["Driver", "Stint"]):
            compound  = str(grp.iloc[0].get("Compound", "")).strip() or None
            start_lap = _safe_int(grp["LapNumber"].min())
            end_lap   = _safe_int(grp["LapNumber"].max())
            stint_rows.append(Stint(
                race_id=race_id,
                driver_id=str(drv).lower(),
                stint_number=_safe_int(stint_num) or 1,
                compound=compound,
                start_lap=start_lap,
                end_lap=end_lap,
            ))
            stints_inserted += 1
        db.bulk_save_objects(stint_rows)
        db.flush()

    # ---- Pit Stops (lap where stint number changes) ----
    pit_stops_inserted = 0
    if "Stint" in laps_df.columns:
        pit_rows = []
        for drv, grp in laps_df.groupby("Driver"):
            grp_sorted = grp.sort_values("LapNumber")
            changes = grp_sorted[grp_sorted["Stint"] != grp_sorted["Stint"].shift(1)]
            for stop_num, (_, pr) in enumerate(changes.iloc[1:].iterrows(), start=1):
                pit_rows.append(PitStop(
                    race_id=race_id,
                    driver_id=str(drv).lower(),
                    stop_number=stop_num,
                    lap=_safe_int(pr.get("LapNumber")),
                    duration_ms=_safe_float(pr.get("PitInTime")),
                ))
                pit_stops_inserted += 1
        db.bulk_save_objects(pit_rows)
        db.flush()

    # ---- Race Results ----
    if not results_df.empty:
        result_rows = []
        for _, row in results_df.iterrows():
            abbr = str(row.get("Abbreviation", "")).strip()
            if not abbr:
                continue
            driver_id = abbr.lower()
            # ClassifiedPosition is a string: "1","2",... or "R","D","W" for retirements
            classified = str(row.get("ClassifiedPosition", "")).strip()
            position = int(classified) if classified.isdigit() else None
            grid = _safe_int(row.get("GridPosition"))
            points = _safe_float(row.get("Points")) or 0.0
            status = str(row.get("Status", "")).strip() or None
            result_rows.append(RaceResult(
                race_id=race_id,
                driver_id=driver_id,
                position=position,
                grid=grid,
                points=points,
                status=status,
                fastest_lap_rank=None,
                fastest_lap_time_ms=None,
            ))
        db.bulk_save_objects(result_rows)
        db.flush()

    # ---- Standings + Race Results via Jolpica (best-effort) ----
    _ingest_from_jolpica(db, season, round_number, race_id)

    db.commit()
    logger.info(
        f"Done: {laps_inserted} laps, {stints_inserted} stints, {pit_stops_inserted} pit stops"
    )
    return {
        "message": f"Ingested {race_name} {season} Round {round_number}",
        "race_id": race_id,
        "laps_inserted": laps_inserted,
        "stints_inserted": stints_inserted,
        "pit_stops_inserted": pit_stops_inserted,
    }


def _ingest_from_jolpica(db: Session, season: int, round_number: int, race_id: int):
    """
    Fetch race results, driver standings, and constructor standings
    from Jolpica (the Ergast replacement API). Covers all seasons including 2024+.
    """
    base = "https://api.jolpi.ca/ergast/f1"
    try:
        with httpx.Client(timeout=20) as client:

            # ---- Race Results (positions + points + grid) ----
            r = client.get(f"{base}/{season}/{round_number}/results.json")
            r.raise_for_status()
            races = r.json().get("MRData", {}).get("RaceTable", {}).get("Races", [])
            if races:
                # Clear existing results for this race then re-insert
                db.query(RaceResult).filter(RaceResult.race_id == race_id).delete()
                db.flush()
                for entry in races[0].get("Results", []):
                    drv_code  = entry["Driver"].get("code", "???").lower()
                    drv_id    = entry["Driver"].get("driverId", drv_code)
                    # Ensure driver exists
                    if not db.get(Driver, drv_code):
                        team_name = entry["Constructor"]["name"]
                        team_id   = _upsert_constructor(db, team_name, team_name)
                        _upsert_driver(
                            db, drv_code,
                            entry["Driver"].get("code", "???"),
                            f"{entry['Driver'].get('givenName','')} {entry['Driver'].get('familyName','')}".strip(),
                            _safe_int(entry["Driver"].get("permanentNumber")),
                            team_id,
                        )
                    # Fastest lap info (optional field in results)
                    fl      = entry.get("FastestLap", {})
                    fl_rank = _safe_int(fl.get("rank"))
                    fl_time = None
                    if fl.get("Time", {}).get("time"):
                        try:
                            parts = fl["Time"]["time"].split(":")
                            fl_time = (float(parts[0]) * 60 + float(parts[1])) * 1000
                        except Exception:
                            pass
                    db.add(RaceResult(
                        race_id=race_id,
                        driver_id=drv_code,
                        position=_safe_int(entry.get("position")),
                        grid=_safe_int(entry.get("grid")),
                        points=float(entry.get("points", 0)),
                        status=entry.get("status") or None,
                        fastest_lap_rank=fl_rank,
                        fastest_lap_time_ms=fl_time,
                    ))
                db.flush()
                logger.info(f"Race results loaded from Jolpica: {len(races[0].get('Results', []))} drivers")

            # ---- Driver Standings ----
            r = client.get(f"{base}/{season}/{round_number}/driverStandings.json")
            r.raise_for_status()
            sl = (
                r.json().get("MRData", {})
                 .get("StandingsTable", {})
                 .get("StandingsLists", [])
            )
            if sl:
                db.query(DriverStanding).filter(
                    DriverStanding.season == season,
                    DriverStanding.round == round_number,
                ).delete()
                db.flush()
                for entry in sl[0].get("DriverStandings", []):
                    drv_code = entry["Driver"].get("code", "???").lower()
                    if not db.get(Driver, drv_code):
                        team_name = entry["Constructors"][0]["name"] if entry.get("Constructors") else "Unknown"
                        team_id   = _upsert_constructor(db, team_name, team_name)
                        drv_data  = entry["Driver"]
                        _upsert_driver(
                            db, drv_code,
                            drv_data.get("code", "???"),
                            f"{drv_data.get('givenName','')} {drv_data.get('familyName','')}".strip(),
                            _safe_int(drv_data.get("permanentNumber")),
                            team_id,
                        )
                    db.add(DriverStanding(
                        season=season,
                        round=round_number,
                        driver_id=drv_code,
                        position=int(entry.get("position", 0)),
                        points=float(entry.get("points", 0)),
                        wins=int(entry.get("wins", 0)),
                    ))
                db.flush()
                logger.info(f"Driver standings loaded: {len(sl[0].get('DriverStandings', []))} entries")

            # ---- Constructor Standings ----
            r = client.get(f"{base}/{season}/{round_number}/constructorStandings.json")
            r.raise_for_status()
            sl = (
                r.json().get("MRData", {})
                 .get("StandingsTable", {})
                 .get("StandingsLists", [])
            )
            if sl:
                db.query(ConstructorStanding).filter(
                    ConstructorStanding.season == season,
                    ConstructorStanding.round == round_number,
                ).delete()
                db.flush()
                for entry in sl[0].get("ConstructorStandings", []):
                    team_id = _upsert_constructor(
                        db,
                        entry["Constructor"]["constructorId"],
                        entry["Constructor"]["name"],
                    )
                    db.add(ConstructorStanding(
                        season=season,
                        round=round_number,
                        team_id=team_id,
                        position=int(entry.get("position", 0)),
                        points=float(entry.get("points", 0)),
                        wins=int(entry.get("wins", 0)),
                    ))
                db.flush()
                logger.info(f"Constructor standings loaded: {len(sl[0].get('ConstructorStandings', []))} entries")

    except Exception as e:
        logger.warning(f"Could not fetch data from Jolpica: {e}")
