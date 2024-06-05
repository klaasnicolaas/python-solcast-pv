"""Asynchronous Python client for Solcast."""


class SolcastError(Exception):
    """Generic Solcast exception."""


class SolcastConnectionError(SolcastError):
    """Solcast connection exception."""


class SolcastAuthenticationError(SolcastError):
    """Solcast authentication exception."""


class SolcastResultsError(SolcastError):
    """Solcast results exception."""
