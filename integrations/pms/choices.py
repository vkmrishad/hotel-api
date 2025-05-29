from django.db.models import TextChoices


class BookingStatus(TextChoices):
    """Booking status choices."""

    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
