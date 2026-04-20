"""Compute yesterday's snow_in_24h and write it to resorts/{id}/daily_snow.

Primary signal: SNOTEL depth delta (snow_depth_in at ~6am today minus
snow_depth_in at ~6am yesterday). Negative settling is clamped to 0.

Fallback when SNOTEL history is too thin: Open-Meteo's daily snow_in for
"yesterday" from the current forecast snapshot (the first entry in daily[]
covers today; we walk the hourly series for yesterday's 24h totals).

This job is idempotent — re-running it on the same day overwrites yesterday's
doc with whatever the best signal currently says.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import structlog

from ..config import load_resorts
from ..firestore_io import (
    daily_snow_collection,
    forecast_snapshot_doc,
    snotel_obs_collection,
)

log = structlog.get_logger()


def run() -> None:
    resorts = load_resorts()
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()

    for r in resorts:
        snow_24h, source = _compute_snow_24h(r.resort_id, yesterday)
        if source == "unavailable":
            log.info(
                "skipped_no_signal",
                resort_id=r.resort_id,
                date=yesterday.isoformat(),
                hint="backfill_daily output preserved",
            )
            continue

        depth, swe = _latest_depth_swe(r.resort_id)
        doc = {
            "date": yesterday.isoformat(),
            "snow_in_24h": snow_24h,
            "source": source,
            "snow_depth_in": depth,
            "swe_in": swe,
            "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        daily_snow_collection(r.resort_id).document(yesterday.isoformat()).set(doc)
        log.info(
            "wrote_daily_snow",
            resort_id=r.resort_id,
            date=yesterday.isoformat(),
            snow_in_24h=snow_24h,
            source=source,
        )
    log.info("done")


def _compute_snow_24h(resort_id: str, for_date: date) -> tuple[float, str]:
    """Return (snow_in_24h, source_tag). Prefer SNOTEL delta when possible."""
    delta = _snotel_delta(resort_id, for_date)
    if delta is not None:
        return delta, "snotel_delta"

    om = _open_meteo_yesterday(resort_id, for_date)
    if om is not None:
        return om, "open_meteo_obs"

    return 0.0, "unavailable"


def _snotel_delta(resort_id: str, for_date: date) -> float | None:
    """Pick the snotel_obs closest to {for_date} 06:00 UTC and to the day prior
    06:00 UTC and return the (clamped) depth delta."""
    snaps = list(snotel_obs_collection(resort_id).stream())
    if len(snaps) < 2:
        return None

    target_end = datetime.combine(
        for_date + timedelta(days=1), datetime.min.time()
    ).replace(tzinfo=timezone.utc) + timedelta(hours=6)
    target_start = target_end - timedelta(days=1)

    obs = [s.to_dict() | {"_id": s.id} for s in snaps if s.to_dict()]
    end_obs = _closest_by_time(obs, target_end)
    start_obs = _closest_by_time(obs, target_start)
    if not end_obs or not start_obs:
        return None

    start_depth = start_obs.get("snow_depth_in")
    end_depth = end_obs.get("snow_depth_in")
    if start_depth is None or end_depth is None:
        return None

    return round(max(0.0, end_depth - start_depth), 2)


def _closest_by_time(obs: list[dict], target: datetime) -> dict | None:
    def distance(o: dict) -> float:
        try:
            ts = datetime.fromisoformat(o.get("observed_at", "").replace("Z", "+00:00"))
        except ValueError:
            return float("inf")
        return abs((ts - target).total_seconds())

    return min(obs, key=distance) if obs else None


def _open_meteo_yesterday(resort_id: str, for_date: date) -> float | None:
    """Pull yesterday's daily snow_in from the latest Open-Meteo snapshot."""
    snap = forecast_snapshot_doc(resort_id, "open_meteo").get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    for day in data.get("daily", []):
        if day.get("date") == for_date.isoformat():
            v = day.get("snow_in")
            return float(v) if v is not None else None
    return None


def _latest_depth_swe(resort_id: str) -> tuple[float | None, float | None]:
    from ..firestore_io import snotel_latest_doc

    sn = snotel_latest_doc(resort_id).get()
    if not sn.exists:
        return None, None
    data = sn.to_dict() or {}
    return data.get("snow_depth_in"), data.get("swe_in")
