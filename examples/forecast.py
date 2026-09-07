"""Asynchronous Python client for Solcast."""

import asyncio

from solcast_pv import RooftopForecast, Solcast


async def main() -> None:
    """Show example on getting Solcast data."""
    async with Solcast(token="API_KEY", timezone="Europe/Amsterdam") as client:
        forecast: RooftopForecast = await client.get_rooftop_forecast(
            resource_id="ROOFTOP_RESOURCE_ID"
        )

        print(f"Energy forecast - today: {forecast.total_energy_forecast_today} kWh")
        print(
            f"Energy forecast - curr hour: {forecast.energy_forecast_current_hour} kWh"
        )
        print(
            "Energy forecast - next hour: "
            f"{forecast.energy_forecast_hours_ahead(1)} kWh"
        )
        print(
            "Energy forecast - today remaining: "
            f"{forecast.total_energy_forecast_remaining_today} kWh"
        )
        print()
        print(
            "Energy forecast - total +d1: "
            f"{forecast.total_energy_forecast_days_ahead(1)} kWh"
        )
        print(
            "Energy forecast - total +d2: "
            f"{forecast.total_energy_forecast_days_ahead(2)} kWh"
        )
        print()
        print(f"Power forecast - now: {forecast.power_forecast_now} W")
        print(f"Power forecast - +30m: {forecast.power_forecast_mins_ahead(30)} W")
        print(f"Power forecast - +1hr: {forecast.power_forecast_mins_ahead(60)} W")
        print(f"Power peak forecast - today: {forecast.power_highest_peak_time_today}")
        print(
            "Power peak forecast - tomorrow: "
            f"{forecast.power_highest_peak_time_tomorrow}"
        )


if __name__ == "__main__":
    asyncio.run(main())
