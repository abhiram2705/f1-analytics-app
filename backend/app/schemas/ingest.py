from pydantic import BaseModel


class IngestRequest(BaseModel):
    season: int
    round: int


class IngestResponse(BaseModel):
    message: str
    race_id: int
    laps_inserted: int
    stints_inserted: int
    pit_stops_inserted: int
