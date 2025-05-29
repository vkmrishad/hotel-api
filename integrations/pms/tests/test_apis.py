from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from integrations.base.exceptions import (
    ExternalAPIException,
    ExternalAPINotFound,
    ExternalAPIResponseError,
)
from integrations.pms.mock_data import MOCK_PMS_BOOKINGS


class BookingListAPIViewTestCase(APITestCase):
    """Test cases for BookingListAPIView"""

    def setUp(self):
        self.url = reverse("booking_list")

    @patch("integrations.pms.views.PMSClient")
    def test_get_bookings_success(self, mock_pms_client):
        """Test successful retrieval of all bookings"""
        # Mock the client instance and its method
        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_bookings.return_value = MOCK_PMS_BOOKINGS

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(MOCK_PMS_BOOKINGS))

        # Check serialized data structure
        first_booking = response.data[0]
        self.assertIn("booking_id", first_booking)
        self.assertIn("guest_name", first_booking)
        self.assertIn("check_in", first_booking)
        self.assertIn("check_out", first_booking)
        self.assertIn("room_number", first_booking)
        self.assertIn("status", first_booking)
        self.assertIn("amount", first_booking)

        # Verify field mapping
        self.assertEqual(first_booking["booking_id"], "1001")
        self.assertEqual(first_booking["guest_name"], "Alice Johnson")
        mock_pms_client.assert_called_once()
        mock_client_instance.fetch_bookings.assert_called_once()

    @patch("integrations.pms.views.PMSClient")
    def test_get_bookings_external_api_exception(self, mock_pms_client):
        """Test handling of external API exception"""
        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_bookings.side_effect = ExternalAPIException(
            "API Error"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "API Error")

    @patch("integrations.pms.views.PMSClient")
    def test_get_bookings_external_api_response_error(self, mock_pms_client):
        """Test handling of external API response error"""
        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_bookings.side_effect = ExternalAPIResponseError(
            status.HTTP_502_BAD_GATEWAY, "Simulated PMS API failure"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)
        self.assertIn("Simulated PMS API failure", response.data["error"])

    @patch("integrations.pms.views.PMSClient")
    def test_get_bookings_empty_response(self, mock_pms_client):
        """Test handling of empty bookings response"""
        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_bookings.return_value = []

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.data, [])


class BookingDetailAPIViewTestCase(APITestCase):
    """Test cases for BookingDetailAPIView"""

    def setUp(self):
        self.booking_id = "1001"
        self.url = reverse("booking_detail", kwargs={"booking_id": self.booking_id})
        self.expected_booking = next(
            b for b in MOCK_PMS_BOOKINGS if b["id"] == self.booking_id
        )

    @patch("integrations.pms.views.PMSClient")
    def test_get_booking_by_id_success(self, mock_pms_client):
        """Test successful retrieval of booking by ID"""
        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_booking_by_id.return_value = self.expected_booking

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check serialized data structure and content
        self.assertIn("booking_id", response.data)
        self.assertIn("guest_name", response.data)
        self.assertIn("check_in", response.data)
        self.assertIn("check_out", response.data)
        self.assertIn("room_number", response.data)
        self.assertIn("status", response.data)
        self.assertIn("amount", response.data)

        # Verify field mapping and values
        self.assertEqual(response.data["booking_id"], "1001")
        self.assertEqual(response.data["guest_name"], "Alice Johnson")
        self.assertEqual(response.data["room_number"], "107")
        self.assertEqual(response.data["status"], "confirmed")
        self.assertEqual(response.data["amount"], 850.00)

        mock_pms_client.assert_called_once()
        mock_client_instance.fetch_booking_by_id.assert_called_once_with(
            int(self.booking_id)
        )

    @patch("integrations.pms.views.PMSClient")
    def test_get_booking_by_id_not_found(self, mock_pms_client):
        """Test handling of booking not found"""
        non_existent_id = 9999
        url = reverse("booking_detail", kwargs={"booking_id": non_existent_id})

        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_booking_by_id.side_effect = ExternalAPINotFound(
            f"Booking ID '{non_existent_id}' not found."
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertIn(
            f"Booking ID '{non_existent_id}' not found", response.data["error"]
        )
        mock_client_instance.fetch_booking_by_id.assert_called_once_with(
            non_existent_id
        )

    @patch("integrations.pms.views.PMSClient")
    def test_get_booking_by_id_external_api_exception(self, mock_pms_client):
        """Test handling of general external API exception"""
        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_booking_by_id.side_effect = ExternalAPIException(
            "General API Error"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "General API Error")

    @patch("integrations.pms.views.PMSClient")
    def test_get_booking_by_id_external_api_response_error(self, mock_pms_client):
        """Test handling of external API response error"""
        mock_client_instance = mock_pms_client.return_value
        mock_client_instance.fetch_booking_by_id.side_effect = ExternalAPIResponseError(
            status.HTTP_502_BAD_GATEWAY, "Simulated PMS API failure"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)
        self.assertIn("Simulated PMS API failure", response.data["error"])

    def test_get_booking_by_id_invalid_url_parameter(self):
        """Test with invalid booking ID parameter in URL"""
        # Test with string parameter (this depends on your URL pattern)
        # If your URL expects int but gets string, Django will handle it
        invalid_url = "/api/integrations/pms/bookings/invalid_id/"

        with patch("integrations.pms.views.PMSClient") as mock_pms_client:
            mock_client_instance = mock_pms_client.return_value
            mock_client_instance.fetch_booking_by_id.side_effect = ExternalAPINotFound(
                "Booking ID 'invalid_id' not found."
            )

            response = self.client.get(invalid_url)

            # This might return 404 from Django routing or from our API logic
            # depending on URL pattern configuration
            self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND])
