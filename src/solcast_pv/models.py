"""Asynchronous Python client for Solcast."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo


def _duration(value: str) -> timedelta:
    """Parse a positive ISO 8601 time duration returned by Solcast."""
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value)
    if match is None:
        msg = "Invalid forecast period"
        raise ValueError(msg)
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    if duration <= timedelta(0):
        msg = "Forecast period must be positive"
        raise ValueError(msg)
    return duration


@dataclass
class RooftopForecast:
    """Average power in kW, indexed by the UTC end of each forecast interval."""

    timezone: str
    pv_estimate: dict[datetime, float]
    pv_estimate10: dict[datetime, float]
    pv_estimate90: dict[datetime, float]
    periods: dict[datetime, timedelta] = field(default_factory=dict)

    def _start(self, end: datetime) -> datetime:
        """Return the beginning of a forecast interval."""
        return end - self.periods.get(end, timedelta(minutes=30))

    def _energy(self, begin: datetime, end: datetime) -> float:
        """Integrate overlapping intervals in UTC, returning kWh."""
        begin, end = begin.astimezone(UTC), end.astimezone(UTC)
        total = 0.0
        for timestamp, kw in self.pv_estimate.items():
            overlap = min(timestamp, end) - max(self._start(timestamp), begin)
            if overlap > timedelta(0):
                total += kw * overlap.total_seconds() / 3600
        return round(total, 5)

    def _day_bounds(self, day: date) -> tuple[datetime, datetime]:
        """Return local midnight boundaries, allowing 23- and 25-hour days."""
        zone = ZoneInfo(self.timezone)
        return (
            datetime.combine(day, time.min, zone),
            datetime.combine(day + timedelta(days=1), time.min, zone),
        )

    def now(self) -> datetime:
        """Return the current time in the requested timezone."""
        return datetime.now(tz=ZoneInfo(self.timezone))

    @property
    def total_energy_forecast_today(self) -> float:
        """Return today's forecast energy in kWh."""
        return self.day_energy_forecast(self.now().date())

    def total_energy_forecast_days_ahead(self, day_ahead: int) -> float:
        """Return the forecast energy for a local day in kWh."""
        return self.day_energy_forecast(self.now().date() + timedelta(days=day_ahead))

    @property
    def total_energy_forecast_remaining_today(self) -> float:
        """Return remaining energy today, including the partial current interval."""
        now = self.now()
        return self._energy(now, self._day_bounds(now.date())[1])

    @property
    def power_forecast_now(self) -> int:
        """Return the current forecast power in W."""
        return self.power_forecast_at_time(self.now())

    def power_forecast_mins_ahead(self, minutes: int) -> int:
        """Return forecast power after the given elapsed minutes in W."""
        return self.power_forecast_at_time(
            self.now().astimezone(UTC) + timedelta(minutes=minutes)
        )

    @property
    def power_highest_peak_time_today(self) -> datetime:
        """Return the end of today's peak interval in the requested timezone."""
        return self.power_peak_forecast_time(self.now().date())

    @property
    def power_highest_peak_time_tomorrow(self) -> datetime:
        """Return the end of tomorrow's peak interval in the requested timezone."""
        return self.power_peak_forecast_time(self.now().date() + timedelta(days=1))

    @property
    def energy_forecast_current_hour(self) -> float:
        """Return forecast energy for the next elapsed hour in kWh."""
        return self.energy_forecast_hours_ahead(0)

    def energy_forecast_hours_ahead(self, hours: int) -> float:
        """Return forecast energy for one elapsed hour starting hours from now."""
        begin = self.now().astimezone(UTC) + timedelta(hours=hours)
        return self._energy(begin, begin + timedelta(hours=1))

    def day_energy_forecast(self, specific_day: date) -> float:
        """Return energy for a local calendar day in kWh."""
        return self._energy(*self._day_bounds(specific_day))

    def power_peak_forecast_time(self, specific_day: date) -> datetime:
        """Return the end of the earliest peak interval overlapping a local day."""
        begin, end = (value.astimezone(UTC) for value in self._day_bounds(specific_day))
        candidates = {
            timestamp: kw
            for timestamp, kw in sorted(self.pv_estimate.items())
            if timestamp > begin and self._start(timestamp) < end
        }
        if not candidates:
            msg = "No peak power forecast found"
            raise RuntimeError(msg)
        peak = max(candidates, key=lambda timestamp: candidates[timestamp])
        return peak.astimezone(ZoneInfo(self.timezone))

    def power_forecast_at_time(self, at: datetime) -> int:
        """Return interval power in W, or zero outside the forecast or in gaps."""
        at = at.astimezone(UTC)
        for end, kw in sorted(self.pv_estimate.items()):
            if self._start(end) <= at < end:
                return int(kw * 1000)
        return 0

    @classmethod
    def from_dict(cls, data: dict[str, Any], timezone: str) -> RooftopForecast:
        """Parse forecast intervals, retaining UTC keys across clock changes."""
        ZoneInfo(timezone)
        estimates: dict[datetime, float] = {}
        low: dict[datetime, float] = {}
        high: dict[datetime, float] = {}
        periods: dict[datetime, timedelta] = {}
        for period in data["forecasts"]:
            end = datetime.fromisoformat(period["period_end"])
            if end.tzinfo is None:
                msg = "Forecast timestamps must include a timezone"
                raise ValueError(msg)
            end = end.astimezone(UTC)
            estimates[end] = float(period["pv_estimate"])
            low[end] = float(period["pv_estimate10"])
            high[end] = float(period["pv_estimate90"])
            periods[end] = _duration(period["period"])
        return cls(timezone, dict(sorted(estimates.items())), low, high, periods)


@dataclass
class RooftopSite:
    """Object representing the rooftop site for the Solcast API."""

    name: str
    resource_id: str
    install_date: datetime

    capacity: float
    capacity_dc: float
    azimuth: int
    tilt: int
    loss_factor: float

    @classmethod
    def from_dict(cls: type[RooftopSite], data: dict[str, Any]) -> RooftopSite:
        """Create a new instance of the RooftopSites class from a dictionary."""
        return cls(
            name=data["name"],
            resource_id=data["resource_id"],
            install_date=datetime.fromisoformat(data["install_date"]),
            capacity=data["capacity"],
            capacity_dc=data["capacity_dc"],
            azimuth=data["azimuth"],
            tilt=data["tilt"],
            loss_factor=data["loss_factor"],
        )


@dataclass
class RateLimit:
    """Object representing the rate limit status for the Solcast API."""

    daily_limit: int
    remaining_daily: int
    consumed_daily: int

    @classmethod
    def from_dict(cls: type[RateLimit], data: dict[str, Any]) -> RateLimit:
        """Create a new instance of the RateLimit class from a dictionary."""
        return cls(
            daily_limit=data["daily_limit"],
            remaining_daily=int(data["daily_limit"] - data["daily_limit_consumed"]),
            consumed_daily=data["daily_limit_consumed"],
        )
