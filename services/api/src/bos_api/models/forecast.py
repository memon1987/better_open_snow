from __future__ import annotations

from pydantic import BaseModel


class HourlyPoint(BaseModel):
    t: str
    temp_f: float | None = None
    wind_mph: float | None = None
    snowfall_in: float | None = None
    precip_in: float | None = None
    visibility_mi: float | None = None


class DailyPoint(BaseModel):
    date: str
    snow_in: float | None = None
    temp_hi_f: float | None = None
    temp_lo_f: float | None = None
    wind_mph_max: float | None = None


class NarrativePeriod(BaseModel):
    name: str
    start: str
    end: str
    temp_f: int | None = None
    wind: str | None = None
    short: str
    detailed: str | None = None
    is_daytime: bool = True


class Forecast(BaseModel):
    resort_id: str
    generated_at: str
    hourly: list[HourlyPoint]
    daily: list[DailyPoint]
    narrative: list[NarrativePeriod] = []
    sources: dict[str, str]
    is_demo: bool = False
