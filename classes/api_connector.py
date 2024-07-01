import logging
import requests
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from urllib3.util.retry import Retry
from typing import List, Dict, Any, Optional

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIConnector:
    def __init__(self, api_url: str) -> None:
        """
        Initialise the APIConnector with the given API URL.

        Args:
            api_url (str): The base URL of the API to connect to.
        """
        self.api_url = api_url
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        """
        Initialise a session with retry mechanism.

        Returns:
            requests.Session: Configured session with retry logic.
        """
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('https://', adapter)
        return session

    def _make_request_with_retry(self, method: str, url: str, params: Dict[str, Any]) -> Optional[requests.Response]:
        """
        Make an HTTP request to the specified URL with retry mechanism.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT', etc.).
            url (str): The URL to make the request to.
            params (Dict[str, Any]): The query parameters for the request.

        Returns:
            Optional[requests.Response]: The response object if the request is successful, else None.
        """
        try:
            response = self.session.request(method, url, params=params, timeout=(3, 30))
            response.raise_for_status()
            return response
        except (HTTPError, ConnectionError, Timeout, RequestException) as err:
            logger.error(f"Request error occurred: {err}")
            return None

    def fetch_air_quality_data(self, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch air quality data from the OpenAQ API.

        Args:
            limit (int): The number of results to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the air quality data results.
        """
        params = {'limit': limit, 'page': 1}
        response = self._make_request_with_retry('GET', self.api_url, params)
        if response:
            return response.json().get('results', [])
        return []

    def close(self) -> None:
        """
        Close the session.
        """
        self.session.close()