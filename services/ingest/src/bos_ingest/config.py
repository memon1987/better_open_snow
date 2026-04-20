"""Shared config for ingest jobs.

Loads the 5-resort seed list from packages/shared/resorts.seed.json so both
the ingest CLI and any future schedulers work from the same source of truth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Resort:
    resort_id: str
    name: str
    pass_: str  # "pass" is a reserved word
    state: str
    base_lat: float
    base_lon: float
    base_elevation_ft: int
    summit_elevation_ft: int
    snotel_triplet: str
    timezone: str


def _repo_root() -> Path:
    # services/ingest/src/bos_ingest/config.py → up 5 = repo root
    return Path(__file__).resolve().parents[4]


def load_resorts() -> list[Resort]:
    seed_path = _repo_root() / "packages" / "shared" / "resorts.seed.json"
    raw = json.loads(seed_path.read_text())
    return [
        Resort(
            resort_id=r["resort_id"],
            name=r["name"],
            pass_=r["pass"],
            state=r["state"],
            base_lat=r["base_lat"],
            base_lon=r["base_lon"],
            base_elevation_ft=r["base_elevation_ft"],
            summit_elevation_ft=r["summit_elevation_ft"],
            snotel_triplet=r["snotel_triplet"],
            timezone=r["timezone"],
        )
        for r in raw
    ]
