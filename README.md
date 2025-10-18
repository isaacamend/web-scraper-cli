# web-scraper-cli

A polite, configurable **Python web scraper CLI** that:
- Respects **robots.txt**
- Supports **same-domain crawling** with a page limit
- Adds **rate limiting** and retries
- Caches pages to speed up development
- Exports results to **CSV and/or JSON**
- Includes **pytest** tests and **GitHub Actions CI**

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Basic: scrape a single page
python -m scraper.cli https://example.com

# Crawl same-domain (up to 10 pages), save CSV+JSON to ./data/
python -m scraper.cli https://example.com --same-domain --max-pages 10 --formats csv json --out data

# Force refetch (ignore cache) and delay 1s between requests
python -m scraper.cli https://example.com --force --delay 1.0
```

## What it extracts
- Page `title`
- All `<a>` links (absolute, deduplicated)

## Command reference
```bash
python -m scraper.cli URL [--same-domain] [--max-pages N] [--delay SECONDS]
                         [--out DIR] [--formats csv json] [--force]
                         [--user-agent UA] [--timeout SECONDS]
```

## Run tests
```bash
pytest -q
```

## Notes
- Always ensure you have permission to scrape a site. Follow the site's robots.txt and terms.
- Default user-agent is a simple identifier; you may customize with `--user-agent`.
