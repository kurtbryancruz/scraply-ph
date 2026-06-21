from bs4 import BeautifulSoup
from typing import List
from .base import BaseParser
from ..registry import ParserRegistry

BASE_URL = "https://www.jobstreet.com.ph"


@ParserRegistry.register("jobstreet")
class JobStreetParser(BaseParser):
    source = "JobStreet"

    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        slug = keyword.strip().replace(" ", "-")
        loc = f"-in-{location.strip().replace(' ', '-')}" if location else ""
        return f"{BASE_URL}/{slug}-jobs{loc}?pg={page}"

    def parse(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("article[data-automation='normalJob']"):
            job = self._base_job()

            title_el = card.select_one("a[data-automation='jobTitle']")
            job["title"] = title_el.get_text(strip=True) if title_el else None
            job["url"] = (BASE_URL + title_el["href"]) if title_el and title_el.get("href") else None

            company_el = card.select_one("a[data-automation='jobCompany']")
            job["company"] = company_el.get_text(strip=True) if company_el else None

            location_el = card.select_one("a[data-automation='jobLocation']")
            job["location"] = location_el.get_text(strip=True) if location_el else None

            salary_el = card.select_one("span[data-automation='jobSalary']")
            job["salary"] = salary_el.get_text(strip=True) if salary_el else None

            jobs.append(job)

        return jobs
