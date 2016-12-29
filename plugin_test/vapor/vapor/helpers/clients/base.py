import logging

LOGGER = logging.getLogger(__name__)


class ContrailBaseClient(object):
    """Contrail base HTTP client."""

    def __init__(self, session, contrail_endpoint):
        """Create ContrailClient object.

        Args:
            session (obj): keystone session
            contrail_endpoint (str): contrail endpoint
        """
        LOGGER.debug('[ContrailClient:__init__]')
        self._endpoint = contrail_endpoint
        self._client = session

    def __enter__(self):
        LOGGER.debug('[ContrailClient:__enter__]')
        return self

    def __exit__(self, type, value, traceback):
        LOGGER.debug('[ContrailClient:__exit__]')
        pass

    @property
    def client(self):
        """Client property."""
        return self._client

    def _request(self, url, method, **kwargs):
        """Send HTTP request."""
        url = self._endpoint.rstrip('/') + url
        return self.client.request(url=url, method=method, **kwargs)

    def _get(self, url, **kwargs):
        """Get method."""
        return self._request(url, 'GET', **kwargs).json()

    def _delete(self, url, **kwargs):
        """Delete method."""
        return self._request(url, 'DELETE', **kwargs).json()

    def _post(self, url, **kwargs):
        """Post method."""
        return self._request(url, 'POST', connect_retries=1, **kwargs).json()

    def _put(self, url, **kwargs):
        """Put method."""
        return self._request(url, 'PUT', connect_retries=1, **kwargs).json()
