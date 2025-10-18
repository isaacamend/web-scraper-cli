from __future__ import annotations
import time, logging, hashlib
from pathlib import Path
from urllib.parse import urlparse
from urllib import robotparser

import requests
from bs4 import BeautifulSoup

from .utils import normalize_url, dedupe, same_domain

log = logging.getLogger("scraper")

DEFAULT_HEADERS = {
    "User-Agent": "web-scraper-cli/1.0 (+https://github.com)"
}

class Fetcher:
    def __init__(self, cache_dir: Path, delay: float = 0.0, timeout: float = 10.0, user_agent: str | None = None):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.delay = max(0.0, delay)
        self.timeout = timeout
        self.headers = dict(DEFAULT_HEADERS)
        if user_agent:
            self.headers["User-Agent"] = user_agent

    def _cache_path(self, url: str) -> Path:
        key = hashlib.md5(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key}.html"

    def fetch(self, url: str, force: bool = False) -> str:
        cp = self._cache_path(url)
        if cp.exists() and not force:
            return cp.read_text(encoding="utf-8", errors="ignore")

        if self.delay:
            time.sleep(self.delay)

        for attempt in range(3):
            try:
                r = requests.get(url, headers=self.headers, timeout=self.timeout)
                if 200 <= r.status_code < 300:
                    cp.write_text(r.text, encoding="utf-8")
                    return r.text
                else:
                    log.warning("HTTP %s for %s", r.status_code, url)
            except requests.RequestException as e:
                log.warning("Request error %s on %s (attempt %d)", e, url, attempt + 1)
            time.sleep(1.0)
        raise RuntimeError(f"Failed to fetch {url} after retries")

def can_fetch(url: str, user_agent: str) -> bool:
    p = urlparse(url)
    robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True

def parse_page(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else "Untitled")
    links = []
    for a in soup.find_all("a"):
        href = a.get("href")
        absu = normalize_url(url, href)
        if absu:
            links.append(absu)
    return {"url": url, "title": title, "links": dedupe(links)}

def crawl(start_url: str, max_pages: int, same_domain_only: bool, fetcher: Fetcher, force: bool=False) -> list[dict]:
    ua = fetcher.headers.get("User-Agent", DEFAULT_HEADERS["User-Agent"])
    results: list[dict] = []
    queue: list[str] = [start_url]
    seen: set[str] = set()

    while queue and len(results) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)

        if not can_fetch(url, ua):
            log.info("robots.txt disallows %s", url)
            continue

        html = fetcher.fetch(url, force=force)
        page = parse_page(url, html)
        results.append(page)

        if same_domain_only:
            for link in page["links"]:
                if same_domain(start_url, link) and link not in seen:
                    queue.append(link)

    return results
