"""Open-Meteo forecast fetcher.

Free, no API key. Gives hourly + daily forecasts for any lat/lon. We pull it
primarily for snowfall amounts, which NWS doesn't surface cleanly.

Docs: https://open-meteo.com/en/docs
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

API_URL = "https://api.open-meteo.com/v1/forecast"
CM_PER_INCH = 2.54
MM_PER_INCH = 25.4
KM_PER_MILE = 1.609344

HOURLY_VARS = "temperature_2m,snowfall,precipitation,wind_speed_10m,visibility"
DAILY_VARS = "snowfall_sum,temperature_2m_max,temperature_2m_min,wind_speed_10m_max"


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def _get(client: httpx.Client, params: dict) -> dict:
    resp = client.get(API_URL, params=params, timeout=20.0)
    resp.raise_for_status()
    return resp.json()


def fetch(lat: float, lon: float, forecast_days: int = 10) -> dict:
    """Fetch a 10-day forecast for a lat/lon and return the snapshot dict.

    Returns the exact shape written to resorts/{id}/forecast_snapshots/open_meteo.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": HOURLY_VARS,
        "daily": DAILY_VARS,
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "UTC",
        "forecast_days": forecast_days,
    }
    with httpx.Client() as client:
        raw = _get(client, params)

    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    hourly = _transform_hourly(raw.get("hourly", {}))
    daily = _transform_daily(raw.get("daily", {}))

    return {
        "source": "open_meteo",
        "fetched_at": fetched_at,
        "hourly": hourly,
        "daily": daily,
    }


def _transform_hourly(h: dict) -> list[dict]:
    times = h.get("time") or []
    temps = h.get("temperature_2m") or []
    snows_cm = h.get("snowfall") or []
    # precipitation comes back in inches because we asked for precipitation_unit=inch
    precips_in = h.get("precipitation") or []
    winds_mph = h.get("wind_speed_10m") or []
    # visibility is always in meters per API
    vis_m = h.get("visibility") or []

    out: list[dict] = []
    for i, t in enumerate(times):
        out.append(
            {
                "t": _isoformat_z(t),
                "temp_f": _safe_float(temps, i),
                "wind_mph": _safe_float(winds_mph, i),
                # snowfall is cm from Open-Meteo; convert to inches
                "snowfall_in": _cm_to_in(_safe_float(snows_cm, i)),
                "precip_in": _safe_float(precips_in, i),
                "visibility_mi": _m_to_mi(_safe_float(vis_m, i)),
            }
        )
    return out


def _transform_daily(d: dict) -> list[dict]:
    dates = d.get("time") or []
    snows_cm = d.get("snowfall_sum") or []
    hi = d.get("temperature_2m_max") or []
    lo = d.get("temperature_2m_min") or []
    wmax = d.get("wind_speed_10m_max") or []

    out: list[dict] = []
    for i, day in enumerate(dates):
        out.append(
            {
                "date": day,  # already YYYY-MM-DD
                "snow_in": _cm_to_in(_safe_float(snows_cm, i)),
                "temp_hi_f": _safe_float(hi, i),
                "temp_lo_f": _safe_float(lo, i),
                "wind_mph_max": _safe_float(wmax, i),
            }
        )
    return out


def _safe_float(xs: list, i: int) -> float | None:
    if i >= len(xs):
        return None
    v = xs[i]
    return float(v) if v is not None else None


def _cm_to_in(v: float | None) -> float | None:
    return round(v / CM_PER_INCH, 2) if v is not None else None


def _m_to_mi(v: float | None) -> float | None:
    return round(v / 1000.0 / KM_PER_MILE, 2) if v is not None else None


def _isoformat_z(t: str) -> str:
    """Open-Meteo returns '2026-04-20T12:00' (no tz) in requested timezone.
    We asked for UTC, so append 'Z'."""
    if t.endswith("Z") or "+" in t:
        return t
    return f"{t}:00Z" if len(t) == 16 else f"{t}Z"
