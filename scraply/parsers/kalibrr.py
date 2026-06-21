import json
import random
import time
from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .base import BaseParser
from ..registry import ParserRegistry

BASE_URL = "https://www.kalibrr.com"

_STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
window.chrome = {runtime: {}};
"""

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


@ParserRegistry.register("kalibrr")
class KalibrrParser(BaseParser):
    source = "Kalibrr"

    def build_url(self, keyword: str, location: str = "", page: int = 1) -> str:
        # Kalibrr search is done via interactive form; this URL is only a hint
        # and is not used directly — see scrape() below.
        return BASE_URL + "/"

    def scrape(self, keyword: str, location: str = "", page: int = 1) -> List[dict]:
        """
        Kalibrr renders results client-side after a form submission.
        We drive a headless browser to submit the search, wait for the
        Next.js router to update the page, then parse __NEXT_DATA__.
        """
        html = self._fetch_via_playwright(keyword, location, page)
        return self.parse(html)

    def _fetch_via_playwright(self, keyword: str, location: str, page: int) -> str:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent=_UA,
                viewport={"width": 1280, "height": 900},
                locale="en-US",
                timezone_id="Asia/Manila",
            )
            ctx.add_init_script(_STEALTH_JS)
            pg = ctx.new_page()

            try:
                pg.goto(BASE_URL + "/", timeout=30_000, wait_until="domcontentloaded")
                time.sleep(random.uniform(1.5, 2.5))

                inp = pg.query_selector("input[placeholder='Job Position']")
                if not inp:
                    raise RuntimeError("Kalibrr search input not found on homepage")

                inp.fill(keyword)
                time.sleep(0.5)

                btn = pg.query_selector("form button")
                if btn:
                    btn.click()
                else:
                    pg.keyboard.press("Enter")

                # Wait for Next.js to fetch and render the search results
                time.sleep(random.uniform(5.0, 7.0))

                # Handle page > 1 by clicking the Next button that many times
                for _ in range(page - 1):
                    next_btn = pg.query_selector("button[aria-label='Next page'], [class*='next']")
                    if next_btn:
                        next_btn.click()
                        time.sleep(random.uniform(3.0, 5.0))
                    else:
                        break

                html = pg.content()
            finally:
                browser.close()

        return html

    def parse(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        nd_el = soup.find("script", id="__NEXT_DATA__")
        if not nd_el:
            return []

        try:
            nd = json.loads(nd_el.string)
            raw_jobs = nd["props"]["pageProps"]["jobs"]
        except (KeyError, json.JSONDecodeError):
            return []

        jobs = []
        for rj in raw_jobs:
            job = self._base_job()
            job["title"] = rj.get("name")
            job["company"] = rj.get("companyName")

            addr = (rj.get("googleLocation") or {}).get("addressComponents") or {}
            city = addr.get("city", "")
            region = addr.get("region", "")
            job["location"] = f"{city}, {region}".strip(", ") or None

            if rj.get("salaryShown"):
                base = rj.get("baseSalary")
                top = rj.get("maximumSalary")
                curr = rj.get("salaryCurrency", "PHP")
                interval = rj.get("salaryInterval", "month")
                if base and top:
                    job["salary"] = f"{curr} {base:,} - {top:,} per {interval}"
                elif base:
                    job["salary"] = f"{curr} {base:,} per {interval}"

            company_code = rj.get("company", {}).get("code", "")
            job_id = rj.get("id")
            slug = rj.get("slug", "")
            if company_code and job_id:
                job["url"] = f"{BASE_URL}/c/{company_code}/jobs/{job_id}/{slug}"

            jobs.append(job)

        return jobs
