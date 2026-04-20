from __future__ import annotations

from pydantic import BaseModel


class DailySnow(BaseModel):
    date: str
    snow_in_24h: float | None = None
    snow_depth_in: float | None = None
    swe_in: float | None = None
    temp_hi_f: float | None = None
    temp_lo_f: float | None = None
    source: str | None = None


class History(BaseModel):
    resort_id: str
    season_start: str
    season_to_date_in: float
    daily: list[DailySnow]
