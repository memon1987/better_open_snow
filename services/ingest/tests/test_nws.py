"""Unit tests for NWS period parsing.

The trap here is that NWS returns temperature in two shapes:
  1. ``temperature: 28, temperatureUnit: "F"``   (legacy numeric form)
  2. ``temperature: {value: -2.22, unitCode: "wmoUnit:degC"}`` (newer form)

Both must round-trip to an integer F.
"""

from __future__ import annotations

from bos_ingest.sources.nws import _coerce_temp_f, _format_wind


def test_coerce_temp_numeric_fahrenheit():
    period = {"temperature": 28, "temperatureUnit": "F"}
    assert _coerce_temp_f(period) == 28


def test_coerce_temp_numeric_celsius_converts():
    period = {"temperature": 0, "temperatureUnit": "C"}
    assert _coerce_temp_f(period) == 32


def test_coerce_temp_object_celsius_converts():
    period = {"temperature": {"value": 0.0, "unitCode": "wmoUnit:degC"}}
    assert _coerce_temp_f(period) == 32


def test_coerce_temp_object_fahrenheit():
    period = {"temperature": {"value": 32.0, "unitCode": "wmoUnit:degF"}}
    assert _coerce_temp_f(period) == 32


def test_coerce_temp_missing_returns_none():
    assert _coerce_temp_f({}) is None
    assert _coerce_temp_f({"temperature": {"value": None}}) is None


def test_format_wind_combines_direction_and_speed():
    period = {"windDirection": "WSW", "windSpeed": "10 to 15 mph"}
    assert _format_wind(period) == "WSW 10 to 15 mph"


def test_format_wind_handles_empty():
    assert _format_wind({}) == ""
