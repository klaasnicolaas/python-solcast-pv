"""Asynchronous Python client for Solcast."""

from __future__ import annotations

import asyncio

from solcast_pv import RooftopSite, Solcast


async def main() -> None:
    """Show example on getting Rooftop sites - Solcast data."""
    async with Solcast(token="API_KEY") as client:
        rooftops: list[RooftopSite] = await client.get_rooftop_sites()
        print(rooftops)


if __name__ == "__main__":
    asyncio.run(main())
