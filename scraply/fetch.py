import random
import time
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

# Removes the most common bot-detection fingerprints injected before any page script runs.
_STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
window.chrome = {runtime: {}};
"""


class FetchError(Exception):
    """Raised when fetch_page cannot return usable HTML."""


def fetch_page(
    url: str,
    page: int = 1,
    timeout: int = 30_000,
    extra_headers: Optional[dict] = None,
    wait_for: str = "networkidle",
) -> str:
    """
    Load *url* in a headless Chromium browser and return the fully-rendered HTML.

    - Rotates User-Agent on every call.
    - Patches navigator.webdriver and other bot-detection markers before page load.
    - Waits for `wait_for` load state (default: networkidle) so JS has time to render.
    - Adds a random 1-3 s human-like delay after initial load.
    - `page` appends a generic ?page=N fallback if the URL has no pagination param.
    - Raises FetchError with a clear message on timeout or navigation failure.
    """
    if page > 1 and not any(p in url for p in ("page=", "pg=", "start=", "offset=")):
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}page={page}"

    ua = random.choice(_USER_AGENTS)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=ua,
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            timezone_id="Asia/Manila",
            java_script_enabled=True,
        )
        ctx.add_init_script(_STEALTH_JS)

        pg = ctx.new_page()
        if extra_headers:
            pg.set_extra_http_headers(extra_headers)

        try:
            pg.goto(url, timeout=timeout, wait_until="domcontentloaded")
            time.sleep(random.uniform(1.0, 3.0))
            pg.wait_for_load_state(wait_for, timeout=timeout)
            html = pg.content()
        except PlaywrightTimeout:
            raise FetchError(f"Timed out after {timeout}ms loading '{url}'")
        except Exception as exc:
            raise FetchError(f"Failed to load '{url}': {exc}") from exc
        finally:
            browser.close()

    return html


# Kept for backward compatibility — existing parsers call this.
def fetch_html(url: str, headers: Optional[dict] = None, timeout: int = 30) -> str:
    return fetch_page(url, timeout=timeout * 1_000, extra_headers=headers)
