import random
import time
from typing import Dict, List, Union

from django.conf import settings
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_502_BAD_GATEWAY

from integrations.base.clients import BaseAPIClient
from integrations.base.exceptions import ExternalAPINotFound, ExternalAPIResponseError

from .mock_data import MOCK_PMS_BOOKINGS


class PMSClient(BaseAPIClient):
    """
    Client to interact with the Property Management System (PMS) API.
    This class simulates external requests using mock data.
    """

    def __init__(self) -> None:
        super().__init__(base_url=settings.PMS_API_URL)

    def fetch_bookings(self) -> List[Dict]:
        """
        Simulate fetching all bookings from the PMS API.
        """
        return self._simulate_get("/bookings/")

    def fetch_booking_by_id(self, booking_id: str) -> Dict:
        """
        Simulate fetching a specific booking from the PMS API by ID.
        """
        return self._simulate_get(f"/bookings/{booking_id}/")

    def _simulate_get(self, path: str) -> Union[List[Dict], Dict]:
        self._simulate_network_latency()
        self._maybe_fail()

        if path == "/bookings/":
            return MOCK_PMS_BOOKINGS

        if path.startswith("/bookings/"):
            booking_id = path.rstrip("/").split("/")[-1]
            for booking in MOCK_PMS_BOOKINGS:
                if booking["id"] == booking_id:
                    return booking
            raise ExternalAPINotFound(f"Booking ID '{booking_id}' not found.")

        raise ExternalAPIResponseError(
            HTTP_400_BAD_REQUEST, f"Invalid endpoint: {path}"
        )

    def _simulate_network_latency(self) -> None:
        time.sleep(random.uniform(0.1, 0.3))

    def _maybe_fail(self, failure_rate: float = 0.2) -> None:
        if random.random() < failure_rate:
            raise ExternalAPIResponseError(
                HTTP_502_BAD_GATEWAY, "Simulated PMS API failure."
            )
