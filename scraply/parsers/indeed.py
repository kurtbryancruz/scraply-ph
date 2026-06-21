from bs4 import BeautifulSoup
from typing import List
from .base import BaseParser
from ..registry import ParserRegistry

BASE_URL = "https://ph.indeed.com"


@ParserRegistry.register("indeed")
class IndeedParser(BaseParser):
    source = "Indeed"

    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        start = (page - 1) * 10
        q = keyword.strip().replace(" ", "+")
        l = location.strip().replace(" ", "+")
        return f"{BASE_URL}/jobs?q={q}&l={l}&start={start}"

    def parse(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("div.job_seen_beacon"):
            job = self._base_job()

            title_el = card.select_one("h2.jobTitle a")
            job["title"] = title_el.get_text(strip=True) if title_el else None
            href = title_el["href"] if title_el and title_el.get("href") else None
            job["url"] = (BASE_URL + href) if href and href.startswith("/") else href

            company_el = card.select_one("span[data-testid='company-name']")
            job["company"] = company_el.get_text(strip=True) if company_el else None

            location_el = card.select_one("div[data-testid='text-location']")
            job["location"] = location_el.get_text(strip=True) if location_el else None

            salary_el = card.select_one("div[data-testid='attribute_snippet_testid']")
            job["salary"] = salary_el.get_text(strip=True) if salary_el else None

            jobs.append(job)

        return jobs
