from pydantic import BaseModel
from typing import Optional


class LapOut(BaseModel):
    lap_id: int
    race_id: int
    driver_id: str
    lap_number: int
    lap_time_ms: Optional[float]
    s1_ms: Optional[float]
    s2_ms: Optional[float]
    s3_ms: Optional[float]
    compound: Optional[str]
    tyre_life: Optional[int]
    is_personal_best: Optional[bool]
    track_status: Optional[str]
    model_config = {"from_attributes": True}


class FastestLapOut(BaseModel):
    driver_id: str
    driver_code: str
    driver_name: str
    team_id: Optional[str]
    team_name: Optional[str]
    lap_number: int
    lap_time_ms: float
    s1_ms: Optional[float]
    s2_ms: Optional[float]
    s3_ms: Optional[float]
    compound: Optional[str]


class TyreDegradationOut(BaseModel):
    compound: str
    tyre_life: int
    avg_lap_time_ms: float
    sample_count: int


class RacePaceOut(BaseModel):
    driver_id: str
    driver_code: str
    team_id: Optional[str]
    lap_number: int
    rolling_avg_ms: float
