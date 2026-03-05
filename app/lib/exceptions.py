"""General exceptions used in the application."""


class APIError(Exception):
    """Base exception for JSON API client errors."""


class ResourceNotFound(APIError):
    pass
