from pydantic import BaseModel
from typing import Optional


class RaceResultOut(BaseModel):
    driver_id: str
    driver_code: Optional[str]
    driver_name: Optional[str]
    team_id: Optional[str]
    team_name: Optional[str]
    position: Optional[int]
    grid: Optional[int]
    points: Optional[float]
    status: Optional[str]
    fastest_lap_rank: Optional[int]
    fastest_lap_time_ms: Optional[float]


class DriverStandingOut(BaseModel):
    round: int
    driver_id: str
    driver_code: Optional[str]
    driver_name: Optional[str]
    team_id: Optional[str]
    position: Optional[int]
    points: float
    wins: int


class ConstructorStandingOut(BaseModel):
    round: int
    team_id: str
    team_name: Optional[str]
    position: Optional[int]
    points: float
    wins: int
