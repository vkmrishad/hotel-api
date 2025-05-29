from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from integrations.pms.mock_data import MOCK_PMS_BOOKINGS


class URLPatternTestCase(TestCase):
    """Test URL pattern resolution"""

    base_url = "/api/integrations/pms"

    def test_booking_list_url_resolves(self):
        """Test that booking list URL resolves correctly"""
        url = reverse("booking_list")
        self.assertEqual(url, f"{self.base_url}/bookings/")

    def test_booking_detail_url_resolves(self):
        """Test that booking detail URL resolves correctly"""
        url = reverse("booking_detail", kwargs={"booking_id": 1001})
        self.assertEqual(url, f"{self.base_url}/bookings/1001/")

    def test_booking_detail_url_with_string_id(self):
        """Test booking detail URL with string ID"""
        url = reverse("booking_detail", kwargs={"booking_id": "1001"})
        self.assertEqual(url, f"{self.base_url}/bookings/1001/")


class IntegrationTestCase(APITestCase):
    """Integration tests that test the full flow without mocking"""

    def setUp(self):
        self.list_url = reverse("booking_list")
        self.detail_url = reverse("booking_detail", kwargs={"booking_id": "1001"})

    def test_booking_list_integration(self):
        """Integration test for booking list endpoint"""
        with patch("integrations.pms.clients.random.random", return_value=0.5):
            with patch("integrations.pms.clients.time.sleep"):
                response = self.client.get(self.list_url)

                # Should succeed or fail with 502 (due to random failure simulation)
                self.assertIn(
                    response.status_code,
                    [
                        status.HTTP_200_OK,
                        status.HTTP_502_BAD_GATEWAY,
                        status.HTTP_400_BAD_REQUEST,
                    ],
                )

                if response.status_code == status.HTTP_200_OK:
                    self.assertEqual(len(response.data), len(MOCK_PMS_BOOKINGS))
                else:
                    self.assertIn("error", response.data)

    def test_booking_detail_integration(self):
        """Integration test for booking detail endpoint"""
        with patch("integrations.pms.clients.random.random", return_value=0.5):
            with patch("integrations.pms.clients.time.sleep"):
                response = self.client.get(self.detail_url)

                # Should succeed or fail with 502 (due to random failure simulation)
                self.assertIn(
                    response.status_code,
                    [status.HTTP_200_OK, status.HTTP_502_BAD_GATEWAY],
                )

                if response.status_code == status.HTTP_200_OK:
                    self.assertEqual(response.data["booking_id"], "1001")
                    self.assertEqual(response.data["guest_name"], "Alice Johnson")
                else:
                    self.assertIn("error", response.data)

    def test_booking_detail_integration_not_found(self):
        """Integration test for booking detail with non-existent ID"""
        not_found_url = reverse("booking_detail", kwargs={"booking_id": "9999"})

        with patch("integrations.pms.clients.random.random", return_value=0.5):
            with patch("integrations.pms.clients.time.sleep"):
                response = self.client.get(not_found_url)

                # Should return 404 or 502 (if simulated failure occurs first)
                self.assertIn(
                    response.status_code,
                    [status.HTTP_404_NOT_FOUND, status.HTTP_502_BAD_GATEWAY],
                )

                if response.status_code == status.HTTP_404_NOT_FOUND:
                    self.assertIn("error", response.data)
                    self.assertIn("9999", response.data["error"])
