"""Unit tests for the Open-Meteo transformer.

The transformer is deterministic — given a fixture response it must produce
the same output every time. These tests cover the three traps we've hit:
  - cm → in conversion for snowfall
  - m → mi conversion for visibility
  - missing values (None) in parallel arrays
"""

from __future__ import annotations

from bos_ingest.sources.open_meteo import _transform_daily, _transform_hourly


def test_hourly_converts_snow_cm_to_in():
    raw = {
        "time": ["2026-04-20T00:00", "2026-04-20T01:00"],
        "temperature_2m": [30.0, 28.0],
        "wind_speed_10m": [10.0, 12.0],
        "snowfall": [2.54, 5.08],  # cm → should become 1.0", 2.0"
        "precipitation": [0.1, 0.2],  # already in inches
        "visibility": [10000.0, 5000.0],  # meters
    }
    out = _transform_hourly(raw)
    assert out[0]["snowfall_in"] == 1.0
    assert out[1]["snowfall_in"] == 2.0
    assert out[0]["precip_in"] == 0.1
    assert out[0]["temp_f"] == 30.0


def test_hourly_converts_visibility_m_to_mi():
    raw = {
        "time": ["2026-04-20T00:00"],
        "temperature_2m": [30.0],
        "wind_speed_10m": [5.0],
        "snowfall": [0.0],
        "precipitation": [0.0],
        "visibility": [16093.44],  # exactly 10 miles in meters
    }
    out = _transform_hourly(raw)
    assert abs(out[0]["visibility_mi"] - 10.0) < 0.01


def test_hourly_tolerates_missing_values():
    raw = {
        "time": ["2026-04-20T00:00"],
        "temperature_2m": [None],
        "wind_speed_10m": [],
        "snowfall": [None],
        "precipitation": [None],
        "visibility": [None],
    }
    out = _transform_hourly(raw)
    assert out[0]["temp_f"] is None
    assert out[0]["wind_mph"] is None
    assert out[0]["snowfall_in"] is None


def test_daily_shape():
    raw = {
        "time": ["2026-04-20"],
        "snowfall_sum": [25.4],  # 10 inches
        "temperature_2m_max": [42.0],
        "temperature_2m_min": [20.0],
        "wind_speed_10m_max": [18.0],
    }
    out = _transform_daily(raw)
    assert out[0]["date"] == "2026-04-20"
    assert out[0]["snow_in"] == 10.0
    assert out[0]["temp_hi_f"] == 42.0
    assert out[0]["temp_lo_f"] == 20.0
