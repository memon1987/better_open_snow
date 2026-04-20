"""Pull NWS gridpoint narrative forecasts for every resort.

First call per resort resolves /points → (office, x, y) and caches the result
on the resort doc (``resorts/{id}.nws``). Subsequent runs reuse the cached
gridpoint so /points isn't hammered.

Writes to: resorts/{id}/forecast_snapshots/nws (overwritten each run).
"""

from __future__ import annotations

import structlog

from .. import demo_data
from ..config import load_resorts
from ..firestore_io import forecast_snapshot_doc, resort_doc
from ..sources import nws

log = structlog.get_logger()


def run() -> None:
    resorts = load_resorts()
    use_demo = demo_data.enabled()
    if use_demo:
        log.warning("BOS_USE_DEMO_DATA=1 — synthesizing instead of hitting NWS")

    for r in resorts:
        try:
            if use_demo:
                snapshot = demo_data.nws(r.resort_id)
            else:
                doc = resort_doc(r.resort_id)
                resort = doc.get().to_dict() or {}
                grid = resort.get("nws")
                if not grid or not all(k in grid for k in ("office", "x", "y")):
                    log.info("resolving_gridpoint", resort_id=r.resort_id)
                    grid = nws.resolve_gridpoint(r.base_lat, r.base_lon)
                    doc.set({"nws": grid}, merge=True)
                snapshot = nws.fetch_forecast(grid["office"], grid["x"], grid["y"])
        except Exception as e:
            log.error("nws_fetch_failed", resort_id=r.resort_id, err=str(e))
            continue

        forecast_snapshot_doc(r.resort_id, "nws").set(snapshot)
        log.info(
            "wrote_nws",
            resort_id=r.resort_id,
            periods=len(snapshot["periods"]),
        )
    log.info("done")
