import logging
from http import HTTPStatus

from django.conf import settings
from requests import (
    ConnectionError,
    JSONDecodeError,
    Timeout,
    TooManyRedirects,
    codes,
    get,
)

logger = logging.getLogger(__name__)


class ResourceNotFound(Exception):
    pass


class JSONAPIClient:
    """
    A simple JSON API client that can be used to make requests to a JSON API.
    It can be used to add parameters to the request and make GET requests.
    It returns the response as a decoded JSON object or raises an error if the request fails.
    The errors are handled by custom middleware in the app.
    """

    def __init__(self, api_url, defaultHeaders=None, defaultParams=None):
        self.api_url = api_url
        self.headers = (
            {
                "Cache-Control": "no-cache",
                # "Accept": "application/json",  # TODO: This breaks the Rosetta API for some reason, investigate and re-add if possible
            }
            if defaultHeaders is None
            else defaultHeaders
        )
        self.params = {} if defaultParams is None else defaultParams

    def add_parameter(self, key, value):
        self.params[key] = value

    def add_parameters(self, params):
        self.params = self.params | params

    def add_header(self, key, value):
        self.headers[key] = value

    def add_headers(self, headers):
        self.headers = self.headers | headers

    def get(self, path="/", timeout=None) -> dict:
        """Makes a request to the config API. Returns decoded json,
        otherwise raises error"""
        url = f"{self.api_url}/{path.lstrip('/')}"
        try:
            response = get(
                url,
                params=self.params,
                headers=self.headers,
                timeout=timeout,
            )
        except ConnectionError:
            logger.error("JSON API connection error")
            raise Exception("A connection error occured")
        except Timeout:
            logger.error("JSON API timeout")
            raise Exception("The request timed out")
        except TooManyRedirects:
            logger.error("JSON API had too many redirects")
            raise Exception("Too many redirects")
        except Exception as e:
            logger.error(f"Unknown JSON API exception: {e}")
            raise Exception(str(e))
        logger.debug(response.url)
        if response.status_code == codes.ok:
            try:
                return response.json()
            except JSONDecodeError:
                logger.error("JSON API provided non-JSON response")

                # TODO: Consider logging the full response somewhere secure for debugging
                number_of_characters_to_log = 100
                truncated_text = response.text[:number_of_characters_to_log]
                suffix = (
                    " ... [truncated]"
                    if len(response.text) > number_of_characters_to_log
                    else ""
                )
                logger.error(f"Non-JSON response: {truncated_text}{suffix}")

                raise Exception("Non-JSON response provided")

        if response.status_code == HTTPStatus.BAD_REQUEST:
            logger.error(f"Bad request: {response.url}")
            raise Exception("Bad request")
        if response.status_code == HTTPStatus.FORBIDDEN:
            logger.warning("Forbidden")
            raise Exception("Forbidden")
        if response.status_code == HTTPStatus.NOT_FOUND:
            logger.warning("Resource not found")
            raise ResourceNotFound("Resource not found")
        logger.error(f"JSON API responded with {response.status_code}")
        raise Exception("Request failed")


def rosetta_request_handler(uri, params=None, timeout=None) -> dict:
    """Prepares and initiates the api url requested and returns response data"""
    if params is None:
        params = {}
    api_url = settings.ROSETTA_API_URL
    if not api_url:
        raise Exception("ROSETTA_API_URL not set")
    client = JSONAPIClient(api_url)
    client.add_parameters(params)
    data = client.get(uri, timeout=timeout)
    return data
