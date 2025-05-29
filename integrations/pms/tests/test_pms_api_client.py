from unittest.mock import patch

from django.test import TestCase
from rest_framework import status

from integrations.base.exceptions import (
    ExternalAPINotFound,
    ExternalAPIResponseError,
)
from integrations.pms.clients import PMSClient
from integrations.pms.mock_data import MOCK_PMS_BOOKINGS


class PMSClientTestCase(TestCase):
    """Test cases for PMSClient class"""

    def setUp(self):
        self.client = PMSClient()

    @patch("integrations.pms.clients.time.sleep")
    @patch("integrations.pms.clients.random.random")
    def test_fetch_bookings_success(self, mock_random, mock_sleep):
        """Test successful fetching of all bookings"""
        # Mock random to avoid simulated failures
        mock_random.return_value = 0.5  # Above failure rate of 0.2

        bookings = self.client.fetch_bookings()

        self.assertEqual(len(bookings), len(MOCK_PMS_BOOKINGS))
        self.assertEqual(bookings, MOCK_PMS_BOOKINGS)
        mock_sleep.assert_called_once()

    @patch("integrations.pms.clients.time.sleep")
    @patch("integrations.pms.clients.random.random")
    def test_fetch_bookings_simulated_failure(self, mock_random, mock_sleep):
        """Test simulated API failure when fetching bookings"""
        # Mock random to trigger simulated failure
        mock_random.return_value = 0.1  # Below failure rate of 0.2

        with self.assertRaises(ExternalAPIResponseError) as context:
            self.client.fetch_bookings()

        self.assertEqual(context.exception.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("Simulated PMS API failure", str(context.exception))

    @patch("integrations.pms.clients.time.sleep")
    @patch("integrations.pms.clients.random.random")
    def test_fetch_booking_by_id_success(self, mock_random, mock_sleep):
        """Test successful fetching of booking by ID"""
        mock_random.return_value = 0.5  # Above failure rate

        booking = self.client.fetch_booking_by_id("1001")

        expected_booking = next(b for b in MOCK_PMS_BOOKINGS if b["id"] == "1001")
        self.assertEqual(booking, expected_booking)
        self.assertEqual(booking["guest"], "Alice Johnson")
        mock_sleep.assert_called_once()

    @patch("integrations.pms.clients.time.sleep")
    @patch("integrations.pms.clients.random.random")
    def test_fetch_booking_by_id_not_found(self, mock_random, mock_sleep):
        """Test fetching non-existent booking by ID"""
        mock_random.return_value = 0.5  # Above failure rate

        with self.assertRaises(ExternalAPINotFound) as context:
            self.client.fetch_booking_by_id("9999")

        self.assertIn("Booking ID '9999' not found", str(context.exception))

    @patch("integrations.pms.clients.time.sleep")
    @patch("integrations.pms.clients.random.random")
    def test_fetch_booking_by_id_simulated_failure(self, mock_random, mock_sleep):
        """Test simulated API failure when fetching booking by ID"""
        mock_random.return_value = 0.1  # Below failure rate

        with self.assertRaises(ExternalAPIResponseError) as context:
            self.client.fetch_booking_by_id("1001")

        self.assertEqual(context.exception.status_code, status.HTTP_502_BAD_GATEWAY)

    @patch("integrations.pms.clients.time.sleep")
    @patch("integrations.pms.clients.random.random")
    def test_simulate_get_invalid_endpoint(self, mock_random, mock_sleep):
        """Test invalid endpoint handling"""
        mock_random.return_value = 0.5  # Above failure rate

        with self.assertRaises(ExternalAPIResponseError) as context:
            self.client._simulate_get("/invalid/endpoint/")

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid endpoint", str(context.exception))

    def test_simulate_network_latency(self):
        """Test that network latency simulation is called"""
        with patch("integrations.pms.clients.time.sleep") as mock_sleep:
            with patch("integrations.pms.clients.random.uniform", return_value=0.2):
                self.client._simulate_network_latency()
                mock_sleep.assert_called_once_with(0.2)

    def test_maybe_fail_with_failure(self):
        """Test _maybe_fail when it should fail"""
        with patch("integrations.pms.clients.random.random", return_value=0.1):
            with self.assertRaises(ExternalAPIResponseError):
                self.client._maybe_fail(failure_rate=0.2)

    def test_maybe_fail_without_failure(self):
        """Test _maybe_fail when it should not fail"""
        with patch("integrations.pms.clients.random.random", return_value=0.5):
            # Should not raise an exception
            self.client._maybe_fail(failure_rate=0.2)
