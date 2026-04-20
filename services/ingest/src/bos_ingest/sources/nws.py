"""NWS (National Weather Service) forecast fetcher.

Two-step workflow:
  1. /points/{lat},{lon}         → resolves to a (office, gridX, gridY) tuple
  2. /gridpoints/{office}/{x},{y}/forecast
                                  → 7-day periodic narrative

NWS gives the best human-readable forecast narrative ("Snow showers before
5pm, heavy at times.") which Open-Meteo lacks. Their numeric snowfall,
however, is either missing or noisy — so we use NWS for narrative only and
Open-Meteo for snowfall amounts.

Docs: https://www.weather.gov/documentation/services-web-api
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

POINTS_URL = "https://api.weather.gov/points/{lat},{lon}"
FORECAST_URL = "https://api.weather.gov/gridpoints/{office}/{x},{y}/forecast"

# NWS asks for a contact header on every request.
HEADERS = {
    "User-Agent": "better-open-snow (github.com/memon1987/better_open_snow)",
    "Accept": "application/geo+json",
}


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def _get(client: httpx.Client, url: str) -> dict:
    resp = client.get(url, timeout=20.0, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()


def resolve_gridpoint(lat: float, lon: float) -> dict:
    """Look up the gridpoint (office, x, y) for a lat/lon.

    NWS is strict about coordinate precision — 4 decimals is plenty.
    """
    url = POINTS_URL.format(lat=round(lat, 4), lon=round(lon, 4))
    with httpx.Client() as client:
        raw = _get(client, url)
    props = raw.get("properties", {})
    return {
        "office": props.get("gridId"),
        "x": props.get("gridX"),
        "y": props.get("gridY"),
        "resolved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def fetch_forecast(office: str, x: int, y: int) -> dict:
    """Pull the 7-day narrative forecast for a resolved gridpoint.

    Returns the snapshot dict written to resorts/{id}/forecast_snapshots/nws.
    """
    url = FORECAST_URL.format(office=office, x=x, y=y)
    with httpx.Client() as client:
        raw = _get(client, url)
    periods_raw = raw.get("properties", {}).get("periods", [])

    periods: list[dict] = [
        {
            "name": p.get("name", ""),
            "start": p.get("startTime", ""),
            "end": p.get("endTime", ""),
            "temp_f": _coerce_temp_f(p),
            "wind": _format_wind(p),
            "short": p.get("shortForecast", ""),
            "detailed": p.get("detailedForecast", ""),
            "is_daytime": bool(p.get("isDaytime", False)),
        }
        for p in periods_raw
    ]

    return {
        "source": "nws",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "periods": periods,
    }


def _coerce_temp_f(period: dict) -> int | None:
    """NWS returns temperatures in F by default but newer payloads sometimes
    carry a nested ``temperature`` object with units. Handle both shapes."""
    temp = period.get("temperature")
    if isinstance(temp, (int, float)):
        unit = period.get("temperatureUnit", "F")
        if unit == "C":
            return int(round(temp * 9 / 5 + 32))
        return int(round(temp))
    if isinstance(temp, dict) and "value" in temp:
        val = temp.get("value")
        unit = temp.get("unitCode", "")
        if val is None:
            return None
        if "degC" in unit:
            return int(round(float(val) * 9 / 5 + 32))
        return int(round(float(val)))
    return None


def _format_wind(period: dict) -> str:
    speed = period.get("windSpeed", "")
    direction = period.get("windDirection", "")
    return f"{direction} {speed}".strip()
