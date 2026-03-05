"""General exceptions used in the application."""


class APIError(Exception):
    """Base exception for JSON API client errors."""


class ResourceNotFound(APIError):
    """Raised when the JSON API responds with HTTP 404."""


class NoResultsFound(APIError):
    """Search completed successfully but returned no results."""


class RecordNotFound(APIError):
    """A specific record requested by ID does not exist."""
