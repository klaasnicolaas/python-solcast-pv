"""Test forecast requests and interval calculations without consuming API quota."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from aresponses import ResponsesMockServer

from solcast_pv import (
    RooftopForecast,
    Solcast,
    SolcastRateLimitError,
    SolcastResultsError,
)

from . import load_fixtures


def period(end: str, power: float = 2, duration: str = "PT30M") -> dict[str, Any]:
    """Build a forecast interval with distinct uncertainty values."""
    return {
        "period_end": end,
        "period": duration,
        "pv_estimate": power,
        "pv_estimate10": power / 2,
        "pv_estimate90": power * 2,
    }


async def test_forecast_request(
    aresponses: ResponsesMockServer, solcast_client: Solcast
) -> None:
    """Fetch exactly one forecast using the requested horizon and parse the fixture."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites/test/forecasts?format=json&hours=24",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("forecast.json"),
        ),
        match_querystring=True,
    )
    forecast = await solcast_client.get_rooftop_forecast("test", hours=24)
    assert len(forecast.pv_estimate) == 97
    assert forecast.pv_estimate[datetime(2024, 6, 4, 21, tzinfo=UTC)] == 0
    aresponses.assert_plan_strictly_followed()


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500])
async def test_forecast_http_errors(
    aresponses: ResponsesMockServer, solcast_client: Solcast, status: int
) -> None:
    """Propagate HTTP errors without automatically spending quota on retries."""
    from solcast_pv import SolcastError  # noqa: PLC0415

    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites/test/forecasts",
        "GET",
        aresponses.Response(status=status),
    )
    with pytest.raises(SolcastRateLimitError if status == 429 else SolcastError):
        await solcast_client.get_rooftop_forecast("test")
    aresponses.assert_plan_strictly_followed()


@pytest.mark.parametrize(
    "data", [{}, {"forecasts": None}, {"forecasts": [period("bad")]}]
)
async def test_malformed_forecast(
    aresponses: ResponsesMockServer, solcast_client: Solcast, data: dict[str, Any]
) -> None:
    """Convert malformed response data into a package exception."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites/test/forecasts",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps(data),
        ),
    )
    with pytest.raises(SolcastResultsError):
        await solcast_client.get_rooftop_forecast("test")


def test_intervals_and_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Integrate partial intervals and restrict peak selection to the requested day."""
    now = datetime(2026, 9, 7, 10, 15, tzinfo=UTC)
    forecast = RooftopForecast.from_dict(
        {
            "forecasts": [
                period("2026-09-08T11:00:00Z", 8, "PT1H"),
                period("2026-09-07T11:00:00Z", 4),
                period("2026-09-07T10:30:00Z", 2),
                period("2026-09-07T12:00:00Z", 8, "PT1H"),
            ]
        },
        "UTC",
    )
    monkeypatch.setattr(RooftopForecast, "now", lambda _self: now)
    assert forecast.total_energy_forecast_today == 11
    assert forecast.total_energy_forecast_days_ahead(1) == 8
    assert forecast.total_energy_forecast_remaining_today == 10.5
    assert forecast.energy_forecast_current_hour == 4.5
    assert forecast.energy_forecast_hours_ahead(1) == 6
    assert forecast.power_forecast_now == 2000
    assert forecast.power_forecast_mins_ahead(30) == 4000
    assert forecast.power_highest_peak_time_today == datetime(
        2026, 9, 7, 12, tzinfo=UTC
    )
    assert forecast.power_highest_peak_time_tomorrow == datetime(
        2026, 9, 8, 11, tzinfo=UTC
    )
    assert (
        forecast.power_forecast_at_time(datetime(2026, 9, 7, 10, 30, tzinfo=UTC))
        == 4000
    )
    assert forecast.power_forecast_at_time(datetime(2026, 9, 7, 9, tzinfo=UTC)) == 0
    assert forecast.power_forecast_at_time(datetime(2026, 9, 7, 13, tzinfo=UTC)) == 0
    assert forecast.power_forecast_at_time(datetime(2026, 9, 9, tzinfo=UTC)) == 0
    assert forecast.pv_estimate10[now.replace(minute=30)] == 1
    assert forecast.pv_estimate90[now.replace(minute=30)] == 4


def test_local_midnight_and_empty_forecast() -> None:
    """Assign energy at local midnight to the preceding day and handle empty data."""
    forecast = RooftopForecast.from_dict(
        {"forecasts": [period("2026-09-07T22:00:00Z")]}, "Europe/Amsterdam"
    )
    assert forecast.day_energy_forecast(date(2026, 9, 7)) == 1
    assert forecast.day_energy_forecast(date(2026, 9, 8)) == 0
    assert forecast.power_peak_forecast_time(date(2026, 9, 7)).hour == 0
    assert forecast.now().tzinfo == ZoneInfo("Europe/Amsterdam")
    empty = RooftopForecast.from_dict({"forecasts": []}, "UTC")
    assert empty.day_energy_forecast(date(2026, 9, 7)) == 0
    with pytest.raises(RuntimeError, match="No peak"):
        empty.power_peak_forecast_time(date(2026, 9, 7))


@pytest.mark.parametrize(
    ("day", "hours"), [(date(2026, 3, 29), 23), (date(2026, 10, 25), 25)]
)
def test_daylight_saving(day: date, hours: int) -> None:
    """Count actual elapsed energy on short and long local days without losing folds."""
    zone = ZoneInfo("Europe/Amsterdam")
    start = datetime(day.year, day.month, day.day, tzinfo=zone).astimezone(UTC)
    data = {
        "forecasts": [
            period((start + timedelta(hours=i + 1)).isoformat(), 1, "PT1H")
            for i in range(hours)
        ]
    }
    forecast = RooftopForecast.from_dict(data, "Europe/Amsterdam")
    assert len(forecast.pv_estimate) == hours
    assert forecast.day_energy_forecast(day) == hours


@pytest.mark.parametrize("duration", ["PT", "PT0M", "P1D", "invalid"])
def test_invalid_duration(duration: str) -> None:
    """Reject unsupported or zero-length forecast intervals."""
    with pytest.raises(ValueError, match=r"[Pp]eriod"):
        RooftopForecast.from_dict(
            {"forecasts": [period("2026-09-07T12:00:00Z", duration=duration)]}, "UTC"
        )


def test_naive_timestamp() -> None:
    """Reject timestamps without an explicit offset."""
    with pytest.raises(ValueError, match="timezone"):
        RooftopForecast.from_dict({"forecasts": [period("2026-09-07T12:00:00")]}, "UTC")


def test_seconds_duration_and_old_constructor() -> None:
    """Support second-based intervals and retain positional client arguments."""
    forecast = RooftopForecast.from_dict(
        {"forecasts": [period("2026-09-07T12:00:00Z", duration="PT1800S")]}, "UTC"
    )
    assert forecast.day_energy_forecast(date(2026, 9, 7)) == 1
    client = Solcast("API_KEY", 5)
    assert client.request_timeout == 5
    assert client.timezone == "UTC"
