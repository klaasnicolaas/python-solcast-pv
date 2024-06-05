"""Asynchronous Python client for Solcast."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import (
    SolcastAuthenticationError,
    SolcastConnectionError,
    SolcastError,
    SolcastResultsError,
)
from .models import RateLimit, RooftopSite

VERSION = metadata.version(__package__)


@dataclass
class Solcast:
    """Main class for handling connections with the Solcast API."""

    token: str

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Solcast API.

        Args:
        ----
            uri: Request URI, without '/api/', for example, 'status'.
            method: HTTP method to use.
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the Solcast API.

        Raises:
        ------
            SolcastConnectionError: Error occurred while connecting to Solcast API.
            SolcastError: Unexpected content type response from Solcast API.

        """
        url = URL.build(
            scheme="https",
            host="api.solcast.com.au",
            path="/",
        ).join(URL(uri))

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": f"PythonSolcastPV/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to Solcast API."
            raise SolcastConnectionError(msg) from exception
        except ClientResponseError as exception:
            if exception.status == 401:
                msg = "Invalid API key provided to Solcast API."
                raise SolcastAuthenticationError(msg) from exception
            if exception.status == 403:
                msg = "API key does not have access to the requested resource."
                raise SolcastAuthenticationError(msg) from exception
            if exception.status == 404:
                msg = "Requested resource was not found on Solcast API."
                raise SolcastError(msg) from exception
            msg = "Error occurred while connecting to Solcast API."
            raise SolcastConnectionError(msg) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while connecting to Solcast API."
            raise SolcastConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from Solcast API."
            raise SolcastError(
                msg,
                {"content_type": content_type, "text": text},
            )

        return await response.json()

    async def get_rooftop_sites(self) -> list[RooftopSite]:
        """Get the rooftop sites for the Solcast API.

        Returns
        -------
            RooftopSite: The rooftop site.

        """
        response = await self._request("rooftop_sites")
        try:
            results: list[RooftopSite] = [
                RooftopSite.from_dict(site) for site in response["sites"]
            ]
        except KeyError as exception:
            msg = "No rooftop sites found on your Solcast account."
            raise SolcastResultsError(msg) from exception
        return results

    async def get_ratelimit(self) -> RateLimit:
        """Get the rate limit status for the Solcast API.

        Returns
        -------
            RateLimit: The rate limit status.

        """
        response = await self._request("json/reply/GetUserUsageAllowance")
        return RateLimit.from_dict(response)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Solcast object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
