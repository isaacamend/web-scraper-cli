import responses
from scraper.core import parse_page, Fetcher, crawl
from pathlib import Path

def test_parse_page_extracts_title_and_links():
    html = '<html><head><title>Hello</title></head><body><a href="/x">X</a></body></html>'
    out = parse_page("https://example.com", html)
    assert out["title"] == "Hello"
    assert out["links"][0].startswith("https://example.com")

@responses.activate
def test_crawl_single_page(tmp_path):
    url = "https://example.com/"
    responses.add(responses.GET, url, body="<html><title>Ex</title></html>", status=200)

    fetcher = Fetcher(cache_dir=tmp_path / "cache", delay=0, timeout=5)
    res = crawl(url, max_pages=1, same_domain_only=False, fetcher=fetcher, force=True)
    assert len(res) == 1
    assert res[0]["title"] == "Ex"
