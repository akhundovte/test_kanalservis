import requests

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, RequestException, JSONDecodeError

from typing import Any

__all__ = (
    'Client', 'HTTPError', 'RequestException', 'JSONDecodeError',
    'request_get',
    )


class Client:
    """Simple Client
     wrap over requests with Retry
    """

    RETRY_AFTER_STATUS_CODES = frozenset([502, 503, 504])
    # по умолчанию POST не входит
    RETRY_ALLOWED_METHODS = frozenset(
        ["POST", "HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )

    def __init__(
        self,
        timeout: int = 60,
        max_retries: int = 5,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._session = requests.Session()
        self._setup_session()

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        self._session.close()

    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Any:
        response = self._session.request(
            method=method,
            url=url,
            timeout=self._timeout,
            **kwargs,
            )
        response.raise_for_status()
        return response

    def _setup_session(self) -> None:
        retries = Retry(
            total=self._max_retries,
            backoff_factor=0,  # 0, 10, 20, 40, 80 sec
            status_forcelist=self.RETRY_AFTER_STATUS_CODES,
            allowed_methods=self.RETRY_ALLOWED_METHODS,
            # чтобы после всех попыток поднималась оригинальная ошибка raise_on_status=False
            # по умолчанию True и поднимается RetryError из requests (MaxRetryError из urllib3)
            # из MaxRetryError не получить response, а там может быть полезная информация
            raise_on_status=True,
            )
        self._session.mount('https://', HTTPAdapter(max_retries=retries))
        self._session.mount('http://', HTTPAdapter(max_retries=retries))


def request_get(
    url: str,
    **kwargs
):
    with Client() as client:
        return client.request('get', url, **kwargs)
