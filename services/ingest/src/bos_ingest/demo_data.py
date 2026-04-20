"""Deterministic demo-data generator for sandboxes without network access.

Enable by setting BOS_USE_DEMO_DATA=1. The source modules will return
realistically-shaped snapshots instead of hitting live APIs. Values are
synthetic — reasonable-for-late-April temps and occasional snow — and are
seeded off (resort_id, date) so they're stable within a day.

This exists ONLY for local dev in environments that can't reach api.weather.gov,
api.open-meteo.com, or AWDB. Production and normal dev machines should leave
the env var unset and hit real APIs.
"""

from __future__ import annotations

import hashlib
import os
from datetime import date, datetime, timedelta, timezone


def enabled() -> bool:
    return os.environ.get("BOS_USE_DEMO_DATA") == "1"


def _seed_rand(key: str) -> float:
    """Deterministic 0..1 pseudo-random from a string."""
    h = hashlib.sha256(key.encode()).digest()
    return int.from_bytes(h[:4], "big") / 2**32


def _snow_today(resort_id: str, d: date) -> float:
    """0..4 inches per day, storm-like clusters per resort."""
    r = _seed_rand(f"{resort_id}|snow|{d.isoformat()}")
    # 60% chance of 0, else up to ~4"
    if r < 0.6:
        return 0.0
    return round((r - 0.6) / 0.4 * 4.0, 1)


def _temp_today(resort_id: str, d: date) -> tuple[float, float]:
    """Late-April plausible (hi, lo)F at base elevation for these resorts."""
    r = _seed_rand(f"{resort_id}|temp|{d.isoformat()}")
    hi = 30.0 + r * 25.0  # 30-55
    lo = hi - (10.0 + _seed_rand(f"{resort_id}|delta|{d.isoformat()}") * 10.0)
    return round(hi, 1), round(lo, 1)


def open_meteo(resort_id: str, lat: float, lon: float, forecast_days: int = 10) -> dict:
    """Return a snapshot dict matching the real Open-Meteo transformer output."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    today = now.date()

    hourly: list[dict] = []
    for hours_ahead in range(forecast_days * 24):
        t = now + timedelta(hours=hours_ahead)
        d = t.date()
        daily_snow = _snow_today(resort_id, d)
        # spread the day's snow across 4 hours centered around midday-ish
        hour_factor = 1.0 if 8 <= t.hour <= 16 else 0.2
        hi, lo = _temp_today(resort_id, d)
        # simple diurnal: lo at 6am, hi at 3pm
        temp = lo + (hi - lo) * max(0.0, 1.0 - abs(t.hour - 15) / 10.0)
        hourly.append(
            {
                "t": t.isoformat().replace("+00:00", "Z"),
                "temp_f": round(temp, 1),
                "wind_mph": round(5.0 + _seed_rand(f"{resort_id}|wind|{t.isoformat()}") * 15.0, 1),
                "snowfall_in": round(daily_snow / 24.0 * 6 * hour_factor, 2),
                "precip_in": round(daily_snow / 24.0 * 6 * hour_factor * 0.1, 3),
                "visibility_mi": 10.0 if daily_snow < 0.5 else 3.0,
            }
        )

    daily: list[dict] = []
    for i in range(forecast_days):
        d = today + timedelta(days=i)
        hi, lo = _temp_today(resort_id, d)
        snow = _snow_today(resort_id, d)
        daily.append(
            {
                "date": d.isoformat(),
                "snow_in": snow,
                "temp_hi_f": hi,
                "temp_lo_f": lo,
                "wind_mph_max": round(
                    8.0 + _seed_rand(f"{resort_id}|wmax|{d.isoformat()}") * 20.0, 1
                ),
            }
        )

    return {
        "source": "open_meteo",
        "fetched_at": now.isoformat().replace("+00:00", "Z"),
        "hourly": hourly,
        "daily": daily,
        "_demo": True,  # marker so the API can warn users
    }


def snotel_latest(resort_id: str, triplet: str, base_elevation_ft: int) -> dict:
    """Synthesize a plausible SNOTEL latest-obs doc."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    r = _seed_rand(f"{resort_id}|snotel|{now.date().isoformat()}")
    # Late-April snowpack: 20-100 inches depending on elevation
    depth = round(20.0 + (base_elevation_ft / 11000.0) * 80.0 * r, 1)
    swe = round(depth * 0.35, 1)
    # 0-3 inches of new snow in last 24h
    snow_24h = _snow_today(resort_id, now.date())
    return {
        "observed_at": now.isoformat().replace("+00:00", "Z"),
        "station_triplet": triplet,
        "swe_in": swe,
        "snow_depth_in": depth,
        "snow_24h_in": snow_24h,
        "air_temp_f": round(28.0 + _seed_rand(f"{resort_id}|temp_obs") * 15.0, 1),
        "_demo": True,
    }
