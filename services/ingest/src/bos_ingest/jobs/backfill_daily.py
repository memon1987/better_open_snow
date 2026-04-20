"""One-shot backfill of season history from Open-Meteo's archive API.

Writes resorts/{id}/daily_snow/{date} for every day from the current season
start (Oct 1 of the winter year) up to yesterday. Uses Open-Meteo's
archive endpoint (free, no key):

    https://archive-api.open-meteo.com/v1/archive
        ?latitude=..&longitude=..
        &start_date=2025-10-01&end_date=2026-04-19
        &daily=snowfall_sum,temperature_2m_max,temperature_2m_min

Run once at dogfood time to populate the history chart. Re-running overwrites
each day's doc — safe but wasteful. Skips archive calls entirely in demo mode,
using a deterministic synthesizer instead.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .. import demo_data
from ..config import load_resorts
from ..firestore_io import daily_snow_collection

log = structlog.get_logger()

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def run() -> None:
    resorts = load_resorts()
    season_start = _current_season_start()
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
    use_demo = demo_data.enabled()
    if use_demo:
        log.warning("BOS_USE_DEMO_DATA=1 — synthesizing instead of hitting Open-Meteo archive")
    log.info("backfill_range", start=season_start.isoformat(), end=yesterday.isoformat())

    for r in resorts:
        try:
            if use_demo:
                days = demo_data.season_daily_snow(r.resort_id, season_start, yesterday)
            else:
                days = _fetch_archive(r.base_lat, r.base_lon, season_start, yesterday)
        except Exception as e:
            log.error("backfill_failed", resort_id=r.resort_id, err=str(e))
            continue

        wrote = 0
        batch = daily_snow_collection(r.resort_id)._client.batch()
        count = 0
        for day in days:
            ref = daily_snow_collection(r.resort_id).document(day["date"])
            batch.set(
                ref,
                {
                    "date": day["date"],
                    "snow_in_24h": day["snow_in_24h"],
                    "source": "open_meteo_archive" if not use_demo else "demo",
                    "temp_hi_f": day.get("temp_hi_f"),
                    "temp_lo_f": day.get("temp_lo_f"),
                    "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                },
            )
            count += 1
            wrote += 1
            if count >= 400:
                batch.commit()
                batch = daily_snow_collection(r.resort_id)._client.batch()
                count = 0
        if count:
            batch.commit()

        log.info("wrote_backfill", resort_id=r.resort_id, days=wrote)
    log.info("done")


def _current_season_start() -> date:
    """Ski seasons straddle calendar years. A "winter YYYY-YYYY+1" season
    starts Oct 1 YYYY. On any date from Oct 1 forward, use that year's Oct 1;
    on Sept 30 or earlier, use the prior year's Oct 1.
    """
    today = datetime.now(timezone.utc).date()
    year = today.year if today.month >= 10 else today.year - 1
    return date(year, 10, 1)


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(3))
def _fetch_archive(lat: float, lon: float, start: date, end: date) -> list[dict]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "snowfall_sum,temperature_2m_max,temperature_2m_min",
        "temperature_unit": "fahrenheit",
        "timezone": "UTC",
    }
    with httpx.Client() as client:
        resp = client.get(ARCHIVE_URL, params=params, timeout=30.0)
        resp.raise_for_status()
        raw = resp.json()

    daily = raw.get("daily", {}) or {}
    dates = daily.get("time") or []
    snows_cm = daily.get("snowfall_sum") or []
    hi = daily.get("temperature_2m_max") or []
    lo = daily.get("temperature_2m_min") or []
    out: list[dict] = []
    for i, d in enumerate(dates):
        cm = _safe(snows_cm, i)
        out.append(
            {
                "date": d,
                "snow_in_24h": round(cm / 2.54, 2) if cm is not None else 0.0,
                "temp_hi_f": _safe(hi, i),
                "temp_lo_f": _safe(lo, i),
            }
        )
    return out


def _safe(xs: list, i: int) -> float | None:
    if i >= len(xs):
        return None
    v = xs[i]
    return float(v) if v is not None else None
