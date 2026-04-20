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


def nws(resort_id: str) -> dict:
    """Synthesize a 7-day NWS narrative snapshot."""
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    today = now.date()

    narratives_snowy = [
        "Snow showers, heavy at times",
        "Scattered snow showers in the afternoon",
        "Light snow with blowing winds",
        "Morning snow, clearing by afternoon",
    ]
    narratives_clear = [
        "Mostly sunny",
        "Partly cloudy",
        "Sunny and cool",
        "Clear with light winds",
    ]

    periods: list[dict] = []
    for i in range(14):  # 7 days × day+night
        is_daytime = i % 2 == 0
        day_offset = i // 2
        d = today + timedelta(days=day_offset)
        snow = _snow_today(resort_id, d)
        narratives = narratives_snowy if snow > 0.5 else narratives_clear
        name = (
            ("Today" if day_offset == 0 else d.strftime("%A"))
            if is_daytime
            else ("Tonight" if day_offset == 0 else f"{d.strftime('%A')} Night")
        )
        hi, lo = _temp_today(resort_id, d)
        temp = hi if is_daytime else lo
        start = now + timedelta(hours=i * 12)
        end = start + timedelta(hours=12)
        short = narratives[int(_seed_rand(f"{resort_id}|nar|{i}") * len(narratives))]
        periods.append(
            {
                "name": name,
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z"),
                "temp_f": int(round(temp)),
                "wind": f"W {5 + int(_seed_rand(f'{resort_id}|w|{i}') * 20)} mph",
                "short": short,
                "detailed": f"{short}. Highs near {int(hi)}F, lows near {int(lo)}F.",
                "is_daytime": is_daytime,
            }
        )

    return {
        "source": "nws",
        "fetched_at": now.isoformat().replace("+00:00", "Z"),
        "periods": periods,
        "_demo": True,
    }


def season_daily_snow(resort_id: str, start: date, end: date) -> list[dict]:
    """Generate a deterministic season's daily snow totals for backfill.

    Stats roughly match a mid-range western season: ~200-350" total by April,
    with snow concentrated November through March.
    """
    out: list[dict] = []
    d = start
    while d <= end:
        # Bias storms toward Nov-Mar; late April sees rare events
        month_factor = 1.5 if 11 <= d.month or d.month <= 3 else 0.3
        r = _seed_rand(f"{resort_id}|season|{d.isoformat()}")
        if r < 1.0 - 0.45 * month_factor:
            snow = 0.0
        else:
            snow = round((r - 0.55) / 0.45 * 10.0 * month_factor, 1)
        hi, lo = _temp_today(resort_id, d)
        # Winter months run colder
        if 12 <= d.month or d.month <= 2:
            hi -= 10.0
            lo -= 10.0
        out.append(
            {
                "date": d.isoformat(),
                "snow_in_24h": max(0.0, snow),
                "temp_hi_f": round(hi, 1),
                "temp_lo_f": round(lo, 1),
            }
        )
        d += timedelta(days=1)
    return out


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
