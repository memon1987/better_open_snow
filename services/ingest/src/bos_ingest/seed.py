"""Seed the 5 resort metadata docs into Firestore.

    python -m bos_ingest seed
"""

from __future__ import annotations

from datetime import datetime, timezone

import structlog

from .config import load_resorts
from .firestore_io import resort_doc

log = structlog.get_logger()


def run() -> None:
    resorts = load_resorts()
    now = datetime.now(timezone.utc).isoformat()
    for r in resorts:
        doc = {
            "resort_id": r.resort_id,
            "name": r.name,
            "pass": r.pass_,
            "state": r.state,
            "base": {
                "lat": r.base_lat,
                "lon": r.base_lon,
                "elevation_ft": r.base_elevation_ft,
            },
            "summit": {"elevation_ft": r.summit_elevation_ft},
            "snotel_triplet": r.snotel_triplet,
            "timezone": r.timezone,
            "updated_at": now,
        }
        resort_doc(r.resort_id).set(doc, merge=True)
        log.info("seeded", resort_id=r.resort_id, name=r.name)
    log.info("done", count=len(resorts))
