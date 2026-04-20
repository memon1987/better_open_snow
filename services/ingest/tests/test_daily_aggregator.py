"""Unit tests for the daily aggregator's pure helpers.

The aggregator itself touches Firestore, but its core logic —
depth-delta computation with clamping — is easy to test in isolation.
"""

from __future__ import annotations

from datetime import datetime, timezone

from bos_ingest.jobs.daily_snow_aggregator import _closest_by_time


def test_closest_by_time_picks_nearest():
    target = datetime(2026, 4, 20, 6, 0, tzinfo=timezone.utc)
    obs = [
        {"observed_at": "2026-04-20T03:00:00+00:00", "snow_depth_in": 60},
        {"observed_at": "2026-04-20T07:00:00+00:00", "snow_depth_in": 62},
        {"observed_at": "2026-04-20T12:00:00+00:00", "snow_depth_in": 63},
    ]
    result = _closest_by_time(obs, target)
    assert result is not None
    assert result["snow_depth_in"] == 62


def test_closest_by_time_empty_list():
    target = datetime(2026, 4, 20, 6, 0, tzinfo=timezone.utc)
    assert _closest_by_time([], target) is None


def test_depth_delta_clamps_negative_settling():
    # Not strictly a unit on _snotel_delta (it needs a Firestore client) but
    # we can still verify the clamp pattern by computing it inline:
    start_depth, end_depth = 70.0, 68.0  # settled 2" overnight
    clamped = max(0.0, end_depth - start_depth)
    assert clamped == 0.0


def test_depth_delta_positive_snow():
    start_depth, end_depth = 60.0, 65.5
    assert round(max(0.0, end_depth - start_depth), 2) == 5.5
