from abc import ABC, abstractmethod
from typing import List


class BaseParser(ABC):
    source: str = ""

    @abstractmethod
    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        """Return the search URL for the given parameters."""

    @abstractmethod
    def parse(self, html: str) -> List[dict]:
        """Parse raw HTML and return a list of job dicts."""

    def _base_job(self) -> dict:
        return {
            "title": None,
            "company": None,
            "location": None,
            "salary": None,
            "url": None,
            "source": self.source,
        }
