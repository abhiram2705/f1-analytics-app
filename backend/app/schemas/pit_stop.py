from pydantic import BaseModel
from typing import Optional


class PitStopOut(BaseModel):
    pit_id: int
    race_id: int
    driver_id: str
    driver_code: Optional[str]
    driver_name: Optional[str]
    team_id: Optional[str]
    stop_number: int
    lap: Optional[int]
    duration_ms: Optional[float]
    model_config = {"from_attributes": True}


class StintOut(BaseModel):
    stint_id: int
    race_id: int
    driver_id: str
    driver_code: Optional[str]
    driver_name: Optional[str]
    team_id: Optional[str]
    stint_number: int
    compound: Optional[str]
    start_lap: Optional[int]
    end_lap: Optional[int]
    length: Optional[int]
    model_config = {"from_attributes": True}
