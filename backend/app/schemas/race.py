from pydantic import BaseModel
from datetime import date
from typing import Optional


class SeasonOut(BaseModel):
    year: int
    model_config = {"from_attributes": True}


class CircuitOut(BaseModel):
    circuit_id: str
    name: str
    country: Optional[str]
    city: Optional[str]
    model_config = {"from_attributes": True}


class RaceOut(BaseModel):
    race_id: int
    season: int
    round: int
    name: str
    date: Optional[date]
    circuit: Optional[CircuitOut]
    model_config = {"from_attributes": True}
