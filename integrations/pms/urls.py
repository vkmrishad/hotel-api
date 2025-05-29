from django.urls import path

from .views import BookingDetailAPIView, BookingListAPIView

urlpatterns = [
    path("bookings/", BookingListAPIView.as_view(), name="booking_list"),
    path(
        "bookings/<int:booking_id>/",
        BookingDetailAPIView.as_view(),
        name="booking_detail",
    ),
]
