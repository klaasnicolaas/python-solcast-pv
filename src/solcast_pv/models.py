"""Asynchronous Python client for Solcast."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


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
