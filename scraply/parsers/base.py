from abc import ABC, abstractmethod
from typing import List


class BaseParser(ABC):
    source: str = ""

    @abstractmethod
    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        """Return the search URL for the given parameters."""

    @abstractmethod
    def parse(self, html: str) -> List[dict]:
        """Parse fully-rendered HTML and return a list of job dicts."""

    def scrape(self, keyword: str, location: str = "", page: int = 1) -> List[dict]:
        """
        Fetch + parse in one call. Override this in parsers that need
        interactive browser behavior (form submission, client-side routing, etc.)
        instead of a simple URL fetch.
        """
        from scraply.fetch import fetch_page
        url = self.build_url(keyword, location, page)
        html = fetch_page(url)
        return self.parse(html)

    def _base_job(self) -> dict:
        return {
            "title": None,
            "company": None,
            "location": None,
            "salary": None,
            "url": None,
            "source": self.source,
        }
