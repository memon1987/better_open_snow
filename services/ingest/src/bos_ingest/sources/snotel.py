"""NRCS SNOTEL (AWDB REST) fetcher.

AWDB REST docs: https://wcc.sc.egov.usda.gov/awdbRestApi/swagger-ui/index.html

Endpoints we use:
  GET /data
    stationTriplets=<triplet>
    elements=SNWD,WTEQ,TOBS        # snow depth (in), SWE (in), air temp (F)
    duration=HOURLY
    beginDate=<yyyy-mm-dd>
    endDate=<yyyy-mm-dd>

The API returns a list of stations, each with a `data` array of elements.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

API_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data"


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def _get(client: httpx.Client, params: dict) -> list:
    resp = client.get(API_URL, params=params, timeout=20.0)
    resp.raise_for_status()
    return resp.json()


def fetch_latest(triplet: str) -> dict | None:
    """Fetch the most recent hourly SNWD/WTEQ/TOBS observation for a station.

    Returns None if the station has no data in the last 48 hours (it happens
    — some stations go offline in summer or during equipment failures).
    """
    today = date.today()
    params = {
        "stationTriplets": triplet,
        "elements": "SNWD,WTEQ,TOBS",
        "duration": "HOURLY",
        "beginDate": (today - timedelta(days=2)).isoformat(),
        "endDate": today.isoformat(),
    }
    with httpx.Client() as client:
        raw = _get(client, params)

    if not raw:
        return None
    station = raw[0]
    elements = {e.get("elementCode"): e.get("values", []) for e in station.get("data", [])}

    snow_depth = _latest_value(elements.get("SNWD", []))
    swe = _latest_value(elements.get("WTEQ", []))
    air_temp = _latest_value(elements.get("TOBS", []))

    observed_at = _latest_time(
        elements.get("SNWD", []) or elements.get("WTEQ", []) or elements.get("TOBS", [])
    )
    if observed_at is None:
        return None

    return {
        "observed_at": observed_at,
        "station_triplet": triplet,
        "swe_in": swe,
        "snow_depth_in": snow_depth,
        "air_temp_f": air_temp,
    }


def _latest_value(values: list[dict]) -> float | None:
    """AWDB returns values in chronological order; grab the last non-null."""
    for v in reversed(values):
        if v.get("value") is not None:
            return float(v["value"])
    return None


def _latest_time(values: list[dict]) -> str | None:
    for v in reversed(values):
        if v.get("value") is not None and v.get("date"):
            # AWDB format: "2026-04-20 15:00" (local TZ). Convert to UTC naive→aware isoformat.
            ts = datetime.strptime(v["date"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            return ts.isoformat()
    return None
