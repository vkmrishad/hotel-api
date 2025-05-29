from rest_framework import serializers

from .choices import BookingStatus


class BookingSerializer(serializers.Serializer):
    """
    Maps raw PMS booking fields to internal API representation.
    """

    booking_id = serializers.CharField(source="id")
    guest_name = serializers.CharField(source="guest")
    check_in = serializers.DateField(source="check_in_date")
    check_out = serializers.DateField(source="check_out_date")
    room_number = serializers.CharField(source="room", required=False)
    status = serializers.ChoiceField(
        source="booking_status", choices=BookingStatus.choices
    )
    amount = serializers.FloatField(source="total_price", required=False)
