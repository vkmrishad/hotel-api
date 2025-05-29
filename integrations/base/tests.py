from unittest.mock import Mock, patch

import httpx
from django.test import TestCase
from rest_framework.status import HTTP_404_NOT_FOUND

from integrations.base.clients import BaseAPIClient
from integrations.base.exceptions import (
    ExternalAPIConnectionError,
    ExternalAPIResponseError,
    ExternalAPITimeoutError,
)


class BaseAPIClientTests(TestCase):
    """
    Test suite for the BaseAPIClient class.

    Tests basic HTTP client functionality including URL construction,
    successful requests, error handling, and parameter passing.
    """

    BASE_URL = "https://api.example.com"
    TEST_ENDPOINT = "/test"

    def setUp(self):
        """Initialize test client with base URL."""
        self.api_client = BaseAPIClient(base_url=self.BASE_URL)

    def test_build_url(self):
        """Test URL construction with and without leading slashes."""
        self.assertEqual(
            self.api_client._build_url(self.TEST_ENDPOINT), f"{self.BASE_URL}/test"
        )
        self.assertEqual(self.api_client._build_url("test"), f"{self.BASE_URL}/test")

    def test_base_url_trailing_slash(self):
        """Test base URL normalization by removing trailing slashes."""
        test_cases = [
            (f"{self.BASE_URL}/", self.BASE_URL),
            (self.BASE_URL, self.BASE_URL),
        ]
        for base_url, expected in test_cases:
            with self.subTest(base_url=base_url):
                client = BaseAPIClient(base_url=base_url)
                self.assertEqual(client.base_url, expected)

    def test_get_success(self):
        """Test successful GET request with mock response."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None

        with patch.object(self.api_client.client, "get", return_value=mock_response):
            result = self.api_client.get(self.TEST_ENDPOINT)
            self.assertEqual(result, {"data": "test"})

    def test_get_http_error(self):
        """Test GET request with 404 error response."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = HTTP_404_NOT_FOUND
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )

        with patch.object(self.api_client.client, "get", return_value=mock_response):
            with self.assertRaises(ExternalAPIResponseError) as cm:
                self.api_client.get(self.TEST_ENDPOINT)
            self.assertEqual(cm.exception.status_code, HTTP_404_NOT_FOUND)

    def test_get_timeout(self):
        """Test GET request timeout handling."""
        with patch.object(
            self.api_client.client, "get", side_effect=httpx.ConnectTimeout("Timeout")
        ):
            with self.assertRaises(ExternalAPITimeoutError):
                self.api_client.get(self.TEST_ENDPOINT)

    def test_get_connection_error(self):
        """Test GET request connection error handling."""
        with patch.object(
            self.api_client.client,
            "get",
            side_effect=httpx.RequestError("Connection failed"),
        ):
            with self.assertRaises(ExternalAPIConnectionError):
                self.api_client.get(self.TEST_ENDPOINT)

    def test_get_with_params(self):
        """Test GET request with query parameters."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None

        with patch.object(
            self.api_client.client, "get", return_value=mock_response
        ) as mock_get:
            self.api_client.get(self.TEST_ENDPOINT, params={"key": "value"})
            mock_get.assert_called_once_with(
                f"{self.BASE_URL}/test", params={"key": "value"}
            )
