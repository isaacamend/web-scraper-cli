from __future__ import annotations
import argparse, sys, csv, json, logging
from pathlib import Path
from datetime import datetime

from .core import Fetcher, crawl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Polite web scraper CLI with robots.txt, caching, and rate limiting.")
    ap.add_argument("url", help="Start URL")
    ap.add_argument("--same-domain", action="store_true", help="Crawl within same domain (BFS)")
    ap.add_argument("--max-pages", type=int, default=1, help="Max pages to fetch (default: 1)")
    ap.add_argument("--delay", type=float, default=0.0, help="Seconds to wait between requests")
    ap.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds (default: 10)")
    ap.add_argument("--out", type=Path, default=Path("data"), help="Output directory for CSV/JSON")
    ap.add_argument("--formats", nargs="+", choices=["csv", "json"], default=["csv"], help="Output formats")
    ap.add_argument("--force", action="store_true", help="Ignore cache (force refetch)")
    ap.add_argument("--user-agent", default=None, help="Override User-Agent")
    args = ap.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)

    fetcher = Fetcher(cache_dir=Path("cache"), delay=args.delay, timeout=args.timeout, user_agent=args.user_agent)
    results = crawl(args.url, max_pages=args.max_pages, same_domain_only=args.same_domain, fetcher=fetcher, force=args.force)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = args.out / f"scrape-{ts}"

    if "json" in args.formats:
        (base.with_suffix(".json")).write_text(json.dumps(results, indent=2), encoding="utf-8")

    if "csv" in args.formats:
        with (base.with_suffix(".csv")).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["url", "title", "num_links", "links"])
            for page in results:
                w.writerow([page["url"], page["title"], len(page["links"]), " ".join(page["links"][:50])])

    print(f"Wrote outputs to: {args.out.resolve()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
