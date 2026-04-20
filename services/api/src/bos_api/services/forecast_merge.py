"""Merge Open-Meteo + NWS forecast snapshots into a single API response.

Policy (pinned):
- Snow amounts: Open-Meteo (NWS gridpoint snowfall is frequently missing).
- Temp / wind / visibility per hour: Open-Meteo.
- Human-readable narrative: NWS periods (if available).

Either snapshot may be missing — if only one is present we still return what
we have. ``sources`` tells the client which source each field came from, and
``is_demo`` bubbles up if either snapshot is synthetic.
"""

from __future__ import annotations


def merge(open_meteo: dict | None, nws: dict | None) -> dict:
    hourly = (open_meteo or {}).get("hourly", [])
    daily = (open_meteo or {}).get("daily", [])
    narrative = (nws or {}).get("periods", [])

    sources: dict[str, str] = {}
    if open_meteo:
        sources["snow"] = "open_meteo"
        sources["hourly"] = "open_meteo"
    if nws:
        sources["narrative"] = "nws"
    elif open_meteo:
        sources["narrative"] = "open_meteo"

    generated_at = (open_meteo or nws or {}).get("fetched_at", "")
    is_demo = bool((open_meteo or {}).get("_demo")) or bool((nws or {}).get("_demo"))

    return {
        "generated_at": generated_at,
        "hourly": hourly,
        "daily": daily,
        "narrative": narrative,
        "sources": sources,
        "is_demo": is_demo,
    }
