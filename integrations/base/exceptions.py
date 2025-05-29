class ExternalAPIException(Exception):
    """
    Base exception for all external API-related errors.
    """

    pass


class ExternalAPIResponseError(ExternalAPIException):
    """
    Raised when the external API returns a non-successful response.

    Attributes:
        status_code (int): HTTP status code returned by the API.
        message (str): Optional detailed message.
    """

    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        self.message = message or f"API returned HTTP {status_code}"
        super().__init__(self.message)


class ExternalAPIConnectionError(ExternalAPIException):
    """
    Raised when there is a network connection problem (e.g., DNS failure, refused connection).
    """

    pass


class ExternalAPITimeoutError(ExternalAPIException):
    """
    Raised when an API request times out.
    """

    pass
