"""Pull Open-Meteo forecasts for every resort and write one snapshot per resort.

Writes to: resorts/{id}/forecast_snapshots/open_meteo (doc is overwritten each run).
"""

from __future__ import annotations

import structlog

from .. import demo_data
from ..config import load_resorts
from ..firestore_io import forecast_snapshot_doc
from ..sources import open_meteo

log = structlog.get_logger()


def run() -> None:
    resorts = load_resorts()
    use_demo = demo_data.enabled()
    if use_demo:
        log.warning("BOS_USE_DEMO_DATA=1 — synthesizing instead of hitting Open-Meteo")

    for r in resorts:
        try:
            if use_demo:
                snapshot = demo_data.open_meteo(r.resort_id, r.base_lat, r.base_lon)
            else:
                snapshot = open_meteo.fetch(r.base_lat, r.base_lon)
        except Exception as e:
            log.error("open_meteo_fetch_failed", resort_id=r.resort_id, err=str(e))
            continue

        forecast_snapshot_doc(r.resort_id, "open_meteo").set(snapshot)
        log.info(
            "wrote_open_meteo",
            resort_id=r.resort_id,
            hourly_count=len(snapshot["hourly"]),
            daily_count=len(snapshot["daily"]),
        )
    log.info("done")
