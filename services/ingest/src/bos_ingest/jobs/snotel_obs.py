"""Pull latest SNOTEL observation for each resort's nearest station.

Writes:
  resorts/{id}/snotel/latest           — single doc, overwritten
  resorts/{id}/snotel_obs/{iso_ts}     — historical (for future trend views)
"""

from __future__ import annotations

import structlog

from .. import demo_data
from ..config import load_resorts
from ..firestore_io import snotel_latest_doc, snotel_obs_collection
from ..sources import snotel

log = structlog.get_logger()


def run() -> None:
    resorts = load_resorts()
    use_demo = demo_data.enabled()
    if use_demo:
        log.warning("BOS_USE_DEMO_DATA=1 — synthesizing instead of hitting AWDB")

    for r in resorts:
        try:
            if use_demo:
                obs = demo_data.snotel_latest(r.resort_id, r.snotel_triplet, r.base_elevation_ft)
            else:
                obs = snotel.fetch_latest(r.snotel_triplet)
        except Exception as e:
            log.error("snotel_fetch_failed", resort_id=r.resort_id, err=str(e))
            continue

        if not obs:
            log.warning("snotel_no_data", resort_id=r.resort_id, triplet=r.snotel_triplet)
            continue

        snotel_latest_doc(r.resort_id).set(obs)
        snotel_obs_collection(r.resort_id).document(obs["observed_at"]).set(obs)
        log.info(
            "wrote_snotel",
            resort_id=r.resort_id,
            snow_depth_in=obs.get("snow_depth_in"),
            swe_in=obs.get("swe_in"),
        )
    log.info("done")
