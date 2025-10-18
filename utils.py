from __future__ import annotations
from urllib.parse import urljoin, urlparse
from typing import Iterable, Set

ABSOLUTE_SCHEME = ("http", "https")

def normalize_url(base: str, href: str) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
        return None
    url = urljoin(base, href)
    p = urlparse(url)
    if p.scheme not in ABSOLUTE_SCHEME:
        return None
    url = url.split("#", 1)[0]
    return url

def same_domain(u1: str, u2: str) -> bool:
    p1, p2 = urlparse(u1), urlparse(u2)
    return p1.netloc.lower() == p2.netloc.lower()

def dedupe(seq: Iterable[str]) -> list[str]:
    seen: Set[str] = set()
    out: list[str] = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
