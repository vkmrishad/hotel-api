from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_502_BAD_GATEWAY,
)
from rest_framework.views import APIView

from integrations.base.exceptions import ExternalAPIException, ExternalAPINotFound
from integrations.pms.clients import PMSClient
from integrations.pms.serializers import BookingSerializer


class BookingListAPIView(APIView):
    """
    GET /api/integrations/pms/bookings/

    Fetch all bookings from the external PMS API.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="Get Bookings List",
        responses={
            HTTP_200_OK: BookingSerializer(many=True),
            HTTP_502_BAD_GATEWAY: "Bad Gateway - External API failure",
        },
        tags=["PMS Bookings"],
    )
    def get(self, request):
        client = PMSClient()
        try:
            raw_data = client.fetch_bookings()
            mapped_serializer = BookingSerializer(raw_data, many=True)
            serializer = BookingSerializer(data=mapped_serializer.data, many=True)

            # Validate input
            if not serializer.is_valid():
                # Filter only the entries that have actual errors
                errors = [error for error in serializer.errors if error]
                return Response({"errors": errors}, status=HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=HTTP_200_OK)
        except ExternalAPIException as e:
            return Response({"error": str(e)}, status=HTTP_502_BAD_GATEWAY)


class BookingDetailAPIView(APIView):
    """
    GET /api/integrations/pms/bookings/{booking_id}/

    Fetch a specific booking from the external PMS API.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="Get Booking by ID",
        responses={
            HTTP_200_OK: BookingSerializer,
            HTTP_404_NOT_FOUND: "Booking not found",
            HTTP_502_BAD_GATEWAY: "External API failure",
        },
        tags=["PMS Bookings"],
    )
    def get(self, request, booking_id):
        client = PMSClient()
        try:
            raw_data = client.fetch_booking_by_id(booking_id)
            mapped_serializer = BookingSerializer(raw_data)
            serializer = BookingSerializer(data=mapped_serializer.data)

            # Validate input
            serializer.is_valid(raise_exception=True)

            return Response(serializer.data, status=HTTP_200_OK)
        except ExternalAPINotFound as e:
            return Response({"error": str(e)}, status=HTTP_404_NOT_FOUND)
        except ExternalAPIException as e:
            return Response({"error": str(e)}, status=HTTP_502_BAD_GATEWAY)
