"""Test the models for Solcast."""

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from solcast_pv import RateLimit, Solcast

from . import load_fixtures


async def test_rate_limiting(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    solcast_client: Solcast,
) -> None:
    """Test rate limiting."""
    aresponses.add(
        "api.solcast.com.au",
        "/json/reply/GetUserUsageAllowance",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("ratelimit.json"),
        ),
    )
    response: RateLimit = await solcast_client.get_ratelimit()
    assert response == snapshot


async def test_rooftop_sites(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    solcast_client: Solcast,
) -> None:
    """Test rooftop sites."""
    aresponses.add(
        "api.solcast.com.au",
        "/rooftop_sites",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("rooftop_sites.json"),
        ),
    )
    response = await solcast_client.get_rooftop_sites()
    assert response == snapshot
