from __future__ import annotations

from pydantic import BaseModel


class SnotelObservation(BaseModel):
    station_triplet: str
    observed_at: str
    swe_in: float | None = None
    snow_depth_in: float | None = None
    snow_24h_in: float | None = None
    air_temp_f: float | None = None


class Observations(BaseModel):
    resort_id: str
    snotel: SnotelObservation | None = None
    is_demo: bool = False
