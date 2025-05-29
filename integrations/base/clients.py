from typing import Any, Optional

import httpx

from integrations.base.exceptions import (
    ExternalAPIConnectionError,
    ExternalAPIResponseError,
    ExternalAPITimeoutError,
)


class BaseAPIClient:
    """
    A base HTTP API client for integrating with third-party REST services.

    Handles base URL composition, HTTP GET requests, and standardized
    error handling. Subclasses can use or extend this client to integrate
    with external systems.
    """

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        """
        Initialize the API client.

        Args:
            base_url (str): Base URL of the external API (e.g., https://api.example.com).
            timeout (float): Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=timeout)

    def _build_url(self, path: str) -> str:
        """
        Construct a full URL by joining base URL and relative path.

        Args:
            path (str): Relative endpoint path (e.g., '/bookings/').

        Returns:
            str: Full URL.
        """
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        """
        Send a GET request to the given API path and return the parsed JSON response.

        Args:
            path (str): Relative API path (e.g., '/bookings/').
            params (Optional[dict]): Optional query parameters.

        Returns:
            Any: Parsed JSON response (usually a dict or list).

        Raises:
            ExternalAPIException: If the request fails or returns an error status.
        """
        url = self._build_url(path)
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ExternalAPIResponseError(
                status_code=e.response.status_code, message=str(e)
            )
        except httpx.ConnectTimeout:
            raise ExternalAPITimeoutError("API request timed out")
        except httpx.ReadTimeout:
            raise ExternalAPITimeoutError("API read timed out")
        except httpx.RequestError as e:
            raise ExternalAPIConnectionError(f"API request failed: {str(e)}")
