"""Test exception handling for Solcast."""

from __future__ import annotations

import pytest
from aresponses import ResponsesMockServer

from solcast_pv import (
    Solcast,
    SolcastAuthenticationError,
    SolcastConnectionError,
    SolcastError,
    SolcastResultsError,
)


async def test_status_401(
    aresponses: ResponsesMockServer,
    solcast_client: Solcast,
) -> None:
    """Test status 401 - Unauthorized."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites",
        "GET",
        aresponses.Response(
            status=401,
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(SolcastAuthenticationError):
        await solcast_client.get_rooftop_sites()


async def test_status_403(
    aresponses: ResponsesMockServer,
    solcast_client: Solcast,
) -> None:
    """Test status 403 - Forbidden."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites",
        "GET",
        aresponses.Response(
            status=403,
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(SolcastAuthenticationError):
        await solcast_client.get_rooftop_sites()


async def test_status_404(
    aresponses: ResponsesMockServer,
    solcast_client: Solcast,
) -> None:
    """Test status 404 - Not Found."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites",
        "GET",
        aresponses.Response(
            status=404,
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(SolcastError):
        await solcast_client.get_rooftop_sites()


async def test_status_429(
    aresponses: ResponsesMockServer,
    solcast_client: Solcast,
) -> None:
    """Test status 429 - Too Many Requests."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites",
        "GET",
        aresponses.Response(
            status=429,
            headers={"Content-Type": "application/json"},
        ),
    )
    with pytest.raises(SolcastConnectionError):
        await solcast_client.get_rooftop_sites()


async def test_no_rooftop_sits(
    aresponses: ResponsesMockServer,
    solcast_client: Solcast,
) -> None:
    """Test no rooftop sites."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text="{}",
        ),
    )
    with pytest.raises(SolcastResultsError):
        await solcast_client.get_rooftop_sites()
