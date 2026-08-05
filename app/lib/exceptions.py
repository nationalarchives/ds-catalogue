"""General API exceptions used in the application."""


class APIError(Exception):
    """Base exception for JSON API client errors."""


class APIConnectionError(APIError):
    """Raised when a connection error occurs while calling the JSON API."""


class APITimeoutError(APIError):
    """Raised when a request to the JSON API times out."""


class APIRedirectError(APIError):
    """Raised when the JSON API request encounters too many redirects."""


class APINonJSONResponseError(APIError):
    """Raised when the JSON API returns a non-JSON response."""


class APIBadRequestError(APIError):
    """Raised when the JSON API responds with HTTP 400."""


class APIForbiddenError(APIError):
    """Raised when the JSON API responds with HTTP 403."""


class APIRequestFailedError(APIError):
    """Raised when the JSON API responds with an unexpected non-OK status."""


class APIResourceNotFound(APIError):
    """Raised when the JSON API responds with HTTP 404."""


class CatalogueError(Exception):
    """Base exception for Catalog errors after successful API calls (200)."""


class NoResultsFound(CatalogueError):
    """Search completed successfully but returned no results."""


class RecordNotFound(CatalogueError):
    """A specific record requested by ID does not exist."""


class MissingAPIAttributeError(CatalogueError):
    """Raised when an expected attribute is missing from the API response."""


class MultipleRecordsError(CatalogueError):
    """Raised when the API response contains multiple records when only one was expected."""
