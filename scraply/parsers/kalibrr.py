from bs4 import BeautifulSoup
from typing import List
from .base import BaseParser
from ..registry import ParserRegistry

BASE_URL = "https://www.kalibrr.com"


@ParserRegistry.register("kalibrr")
class KalibrrParser(BaseParser):
    source = "Kalibrr"

    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        q = keyword.strip().replace(" ", "%20")
        loc = location.strip().replace(" ", "%20")
        offset = (page - 1) * 20
        url = f"{BASE_URL}/jobs#/page/{page}?limit=20&offset={offset}&search={q}"
        if loc:
            url += f"&location={loc}"
        return url

    def parse(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("div.k-job-card"):
            job = self._base_job()

            title_el = card.select_one("h2.k-job-card__title a")
            job["title"] = title_el.get_text(strip=True) if title_el else None
            href = title_el["href"] if title_el and title_el.get("href") else None
            job["url"] = (BASE_URL + href) if href and href.startswith("/") else href

            company_el = card.select_one("span.k-job-card__company-name")
            job["company"] = company_el.get_text(strip=True) if company_el else None

            location_el = card.select_one("span.k-job-card__location")
            job["location"] = location_el.get_text(strip=True) if location_el else None

            salary_el = card.select_one("span.k-job-card__salary")
            job["salary"] = salary_el.get_text(strip=True) if salary_el else None

            jobs.append(job)

        return jobs
