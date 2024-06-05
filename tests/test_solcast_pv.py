"""Basic tests for Solcast."""

# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from solcast_pv import Solcast
from solcast_pv.exceptions import SolcastConnectionError, SolcastError

from . import load_fixtures


async def test_json_request(
    aresponses: ResponsesMockServer,
    solcast_client: Solcast,
) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("rooftop_sites.json"),
        ),
    )
    await solcast_client._request("rooftop_sites/test")
    await solcast_client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("rooftop_sites.json"),
        ),
    )
    async with Solcast(token="API_KEY") as client:
        await client._request("rooftop_sites/test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from the Solcast API."""

    # Faking a timeout by sleeping
    async def response_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("rooftop_sites.json"),
        )

    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites/test",
        "GET",
        response_handler,
    )

    async with ClientSession() as session:
        client = Solcast(
            token="API_KEY",
            session=session,
            request_timeout=0.1,
        )
        with pytest.raises(SolcastConnectionError):
            await client._request("rooftop_sites/test")


async def test_content_type(
    aresponses: ResponsesMockServer,
    solcast_client: Solcast,
) -> None:
    """Test incorrect content type is handled correctly."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
        ),
    )
    with pytest.raises(SolcastError):
        assert await solcast_client._request("rooftop_sites/test")


async def test_client_error() -> None:
    """Test client error is handled correctly."""
    async with ClientSession() as session:
        client = Solcast(token="API_KEY", session=session)
        with (
            patch.object(
                session,
                "request",
                side_effect=ClientError,
            ),
            pytest.raises(SolcastConnectionError),
        ):
            assert await client._request("test")
