"""Unit tests for the SNOTEL (AWDB) transformer.

AWDB returns a list of stations, each with a list of elements, each with a
list of hourly values. Any value can be null. We need to pick the most recent
non-null across SNWD/WTEQ/TOBS.
"""

from __future__ import annotations

from bos_ingest.sources.snotel import _latest_time, _latest_value


def test_latest_value_picks_last_non_null():
    values = [
        {"date": "2026-04-20 10:00", "value": 60.0},
        {"date": "2026-04-20 11:00", "value": 61.0},
        {"date": "2026-04-20 12:00", "value": None},
        {"date": "2026-04-20 13:00", "value": 62.0},
        {"date": "2026-04-20 14:00", "value": None},
    ]
    assert _latest_value(values) == 62.0


def test_latest_value_returns_none_when_all_null():
    values = [{"date": "2026-04-20 10:00", "value": None}]
    assert _latest_value(values) is None


def test_latest_value_empty_list():
    assert _latest_value([]) is None


def test_latest_time_parses_iso():
    values = [
        {"date": "2026-04-20 14:00", "value": 50.0},
    ]
    ts = _latest_time(values)
    assert ts is not None
    assert ts.startswith("2026-04-20T14:00")
    assert ts.endswith("+00:00")
