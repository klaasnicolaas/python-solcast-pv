"""Asynchronous Python client for Solcast."""

import asyncio

from solcast_pv import RateLimit, Solcast


async def main() -> None:
    """Show example on getting Rate limit - Solcast data."""
    async with Solcast(token="API_KEY") as client:
        ratelimit: RateLimit = await client.get_ratelimit()

        print(f"Rate limit: {ratelimit.daily_limit}")
        print(f"Rate limit - remaining: {ratelimit.remaining_daily}")
        print(f"Rate limit - consumed: {ratelimit.consumed_daily}")


if __name__ == "__main__":
    asyncio.run(main())
