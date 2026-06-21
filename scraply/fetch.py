import random
import requests
from typing import Optional

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

_BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}


def _build_headers() -> dict:
    return {**_BASE_HEADERS, "User-Agent": random.choice(_USER_AGENTS)}


def fetch_page(url: str, page: int = 1, timeout: int = 15, extra_headers: Optional[dict] = None) -> str:
    """
    Fetch a URL and return raw HTML. Raises FetchError on any failure.

    - Rotates User-Agent on every call to reduce blocking.
    - `page` is passed to the caller's URL-building logic; this function
      appends a `page` query param only when the URL has no existing one
      and page > 1, acting as a generic fallback.
    - Raises FetchError with a clear message for timeouts, connection
      errors, and non-200 HTTP responses.
    """
    if page > 1 and "page=" not in url and "pg=" not in url and "start=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}page={page}"

    headers = _build_headers()
    if extra_headers:
        headers.update(extra_headers)

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError as exc:
        raise FetchError(f"Connection failed for '{url}': {exc}") from exc
    except requests.exceptions.Timeout:
        raise FetchError(f"Request timed out after {timeout}s for '{url}'")
    except requests.exceptions.RequestException as exc:
        raise FetchError(f"Request error for '{url}': {exc}") from exc

    if response.status_code == 403:
        raise FetchError(f"Access denied (403) for '{url}' — site may be blocking scrapers.")
    if response.status_code == 404:
        raise FetchError(f"Page not found (404): '{url}'")
    if response.status_code == 429:
        raise FetchError(f"Rate limited (429) by '{url}' — slow down requests.")
    if not response.ok:
        raise FetchError(f"HTTP {response.status_code} for '{url}'")

    return response.text


class FetchError(Exception):
    """Raised when fetch_page cannot return usable HTML."""


# Kept for backward compatibility with existing parser code.
def fetch_html(url: str, headers: Optional[dict] = None, timeout: int = 15) -> str:
    return fetch_page(url, timeout=timeout, extra_headers=headers)
