"""General exceptions used in the application."""


class APIError(Exception):
    """Base exception for JSON API client errors."""


class ResourceNotFound(APIError):
    """Raised when the JSON API responds with HTTP 404."""


class NoResultsFound(APIError):
    """Search completed successfully but returned no results."""


class RecordNotFound(APIError):
    """A specific record requested by ID does not exist."""


class APIConnectionError(APIError):
    """Raised when a connection error occurs while calling the JSON API."""


class APITimeoutError(APIError):
    """Raised when a request to the JSON API times out."""


class APIRedirectError(APIError):
    """Raised when the JSON API request encounters too many redirects."""
