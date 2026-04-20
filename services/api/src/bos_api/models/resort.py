from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ResortElevation(BaseModel):
    elevation_ft: int


class ResortBase(BaseModel):
    lat: float
    lon: float
    elevation_ft: int


class ResortSummary(BaseModel):
    """Compact row for the list screen."""

    resort_id: str
    name: str
    pass_: Literal["epic", "ikon"] = Field(alias="pass")
    state: str
    base_elevation_ft: int
    summit_elevation_ft: int

    # Headline numbers; null until the relevant ingest job has run.
    latest_snow_24h_in: float | None = None
    snow_depth_in: float | None = None

    model_config = {"populate_by_name": True}


class ResortDetail(BaseModel):
    """Full metadata for the detail screen."""

    resort_id: str
    name: str
    pass_: Literal["epic", "ikon"] = Field(alias="pass")
    state: str
    base: ResortBase
    summit: ResortElevation
    snotel_triplet: str
    timezone: str

    model_config = {"populate_by_name": True}


class ResortList(BaseModel):
    resorts: list[ResortSummary]
