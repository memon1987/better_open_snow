"""Unit tests for forecast_merge.

Policy verified here:
- When both snapshots exist: Open-Meteo supplies hourly/daily, NWS supplies
  narrative.
- When only Open-Meteo exists: narrative falls back to open_meteo.
- When only NWS exists: hourly/daily are empty, narrative from NWS.
- is_demo is OR of both inputs.
"""

from __future__ import annotations

from bos_api.services.forecast_merge import merge

OM = {
    "fetched_at": "2026-04-20T15:00:00Z",
    "hourly": [{"t": "2026-04-20T16:00:00Z", "temp_f": 34.2}],
    "daily": [{"date": "2026-04-20", "snow_in": 3.5}],
}

NWS = {
    "fetched_at": "2026-04-20T14:30:00Z",
    "periods": [{"name": "Today", "temp_f": 35, "short": "Snow showers", "start": "", "end": "", "is_daytime": True}],
}


def test_merge_both_sources():
    m = merge(open_meteo=OM, nws=NWS)
    assert m["hourly"] == OM["hourly"]
    assert m["daily"] == OM["daily"]
    assert m["narrative"] == NWS["periods"]
    assert m["sources"] == {"snow": "open_meteo", "hourly": "open_meteo", "narrative": "nws"}
    assert m["is_demo"] is False


def test_merge_only_open_meteo():
    m = merge(open_meteo=OM, nws=None)
    assert m["narrative"] == []
    assert m["sources"]["narrative"] == "open_meteo"


def test_merge_only_nws():
    m = merge(open_meteo=None, nws=NWS)
    assert m["hourly"] == []
    assert m["daily"] == []
    assert m["narrative"] == NWS["periods"]
    assert m["sources"].get("snow") is None
    assert m["sources"]["narrative"] == "nws"


def test_merge_demo_flag_propagates():
    om_demo = {**OM, "_demo": True}
    m = merge(open_meteo=om_demo, nws=NWS)
    assert m["is_demo"] is True
