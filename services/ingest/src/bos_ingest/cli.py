"""CLI entry point for all ingest jobs.

    python -m bos_ingest <job>

Jobs:
    seed                    Upsert 5 resort metadata docs
    weather_open_meteo      (M4) Pull Open-Meteo forecasts for every resort
    weather_nws             (M5) Pull NWS gridpoint forecasts
    snotel_obs              (M6) Pull latest SNOTEL observations
    daily_snow_aggregator   (M7) Compute season-to-date daily snow
    backfill_daily          (M7) Backfill season history from Open-Meteo archive
"""

from __future__ import annotations

import sys

import structlog

log = structlog.get_logger()


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    job = argv[0]

    if job == "seed":
        from . import seed

        seed.run()
        return 0

    if job == "weather_open_meteo":
        from .jobs import weather_open_meteo

        weather_open_meteo.run()
        return 0

    if job == "weather_nws":
        from .jobs import weather_nws

        weather_nws.run()
        return 0

    if job == "snotel_obs":
        from .jobs import snotel_obs as snotel_obs_job

        snotel_obs_job.run()
        return 0

    if job == "daily_snow_aggregator":
        from .jobs import daily_snow_aggregator

        daily_snow_aggregator.run()
        return 0

    if job == "backfill_daily":
        from .jobs import backfill_daily

        backfill_daily.run()
        return 0

    log.error("unknown job", job=job)
    print(f"Unknown job: {job}\n{__doc__}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
