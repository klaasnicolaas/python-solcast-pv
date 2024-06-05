"""Fixtures for the Solcast tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from solcast_pv import Solcast


@pytest.fixture(name="solcast_client")
async def client() -> AsyncGenerator[Solcast, None]:
    """Return a Solcast client."""
    async with (
        ClientSession() as session,
        Solcast(token="API_KEY", session=session) as solcast_client,
    ):
        yield solcast_client
