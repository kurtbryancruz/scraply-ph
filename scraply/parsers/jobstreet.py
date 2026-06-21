from bs4 import BeautifulSoup
from typing import List
from .base import BaseParser
from ..registry import ParserRegistry

BASE_URL = "https://ph.jobstreet.com"


@ParserRegistry.register("jobstreet")
class JobStreetParser(BaseParser):
    source = "JobStreet"

    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        kw_slug = keyword.strip().replace(" ", "-")
        loc_slug = f"-in-{location.strip().replace(' ', '-')}" if location.strip() else ""
        return f"{BASE_URL}/{kw_slug}-jobs{loc_slug}?pg={page}"

    def parse(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        for card in soup.select("article[data-automation='normalJob']"):
            job = self._base_job()

            title_el = card.select_one("a[href*='origin=cardTitle']")
            if title_el:
                job["title"] = title_el.get_text(strip=True)
                raw_href = title_el.get("href", "")
                # Strip the #sol=... tracking fragment before storing the URL
                clean_href = raw_href.split("#")[0]
                # Also strip the origin= param (cosmetic, not functional)
                if "?" in clean_href:
                    base_path, qs = clean_href.split("?", 1)
                    params = [p for p in qs.split("&")
                              if not p.startswith("origin=") and not p.startswith("ref=")]
                    clean_href = f"{base_path}?{'&'.join(params)}" if params else base_path
                job["url"] = BASE_URL + clean_href if clean_href else None

            company_el = card.select_one("[data-automation='jobCompany']")
            job["company"] = company_el.get_text(strip=True) if company_el else None

            location_el = card.select_one("[data-automation='jobLocation']")
            job["location"] = location_el.get_text(strip=True) if location_el else None

            # Salary is not shown in JobStreet search result cards
            salary_el = card.select_one("[data-automation='jobSalary']")
            job["salary"] = salary_el.get_text(strip=True) if salary_el else None

            jobs.append(job)

        return jobs
