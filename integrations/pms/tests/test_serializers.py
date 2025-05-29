from unittest import TestCase

from integrations.pms.mock_data import MOCK_PMS_BOOKINGS


class SerializerTestCase(TestCase):
    """Test cases for BookingSerializer"""

    def test_booking_serializer_field_mapping(self):
        """Test that BookingSerializer correctly maps fields"""
        from integrations.pms.serializers import BookingSerializer

        sample_booking = MOCK_PMS_BOOKINGS[0]
        serializer = BookingSerializer(sample_booking)

        # Test field mapping
        self.assertEqual(serializer.data["booking_id"], sample_booking["id"])
        self.assertEqual(serializer.data["guest_name"], sample_booking["guest"])
        self.assertEqual(serializer.data["check_in"], sample_booking["check_in_date"])
        self.assertEqual(serializer.data["check_out"], sample_booking["check_out_date"])
        self.assertEqual(serializer.data["room_number"], sample_booking["room"])
        self.assertEqual(serializer.data["status"], sample_booking["booking_status"])
        self.assertEqual(serializer.data["amount"], sample_booking["total_price"])

    def test_booking_serializer_multiple_bookings(self):
        """Test BookingSerializer with multiple bookings"""
        from integrations.pms.serializers import BookingSerializer

        serializer = BookingSerializer(MOCK_PMS_BOOKINGS[:3], many=True)

        self.assertEqual(len(serializer.data), 3)
        for i, booking_data in enumerate(serializer.data):
            original_booking = MOCK_PMS_BOOKINGS[i]
            self.assertEqual(booking_data["booking_id"], original_booking["id"])
            self.assertEqual(booking_data["guest_name"], original_booking["guest"])

    def test_booking_serializer_status_choices(self):
        """Test that BookingSerializer validates status choices correctly"""
        from integrations.pms.serializers import BookingSerializer

        valid_statuses = ["confirmed", "pending", "cancelled"]

        for status_value in valid_statuses:
            sample_booking = MOCK_PMS_BOOKINGS[0].copy()
            sample_booking["booking_status"] = status_value

            serializer = BookingSerializer(sample_booking)
            self.assertEqual(serializer.data["status"], status_value)
