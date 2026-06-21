from bs4 import BeautifulSoup
from typing import List
from .base import BaseParser
from ..registry import ParserRegistry

BASE_URL = "https://ph.indeed.com"


@ParserRegistry.register("indeed")
class IndeedParser(BaseParser):
    source = "Indeed"

    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        q = keyword.strip().replace(" ", "+")
        l = location.strip().replace(" ", "+")
        start = (page - 1) * 10
        return f"{BASE_URL}/jobs?q={q}&l={l}&start={start}"

    def parse(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("div.job_seen_beacon"):
            job = self._base_job()

            # Title lives in an <h3> containing an <a data-jk="...">
            title_a = card.select_one("h3 a[data-jk]")
            if title_a:
                job["title"] = title_a.get_text(strip=True)
                href = title_a.get("href", "")
                job["url"] = (BASE_URL + href) if href.startswith("/") else href or None

            company_el = card.select_one("[data-testid='company-name']")
            job["company"] = company_el.get_text(strip=True) if company_el else None

            location_el = card.select_one("[data-testid='text-location']")
            job["location"] = location_el.get_text(strip=True) if location_el else None

            salary_el = card.select_one("[class*='salary-snippet']")
            job["salary"] = salary_el.get_text(strip=True) if salary_el else None

            jobs.append(job)

        return jobs
