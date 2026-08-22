#!/usr/bin/env py -3
"""Verify article image URLs resolve before deploy."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]


def check_url(url: str) -> bool:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status < 400
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def main() -> int:
    data = json.loads((SITE / "data" / "articles.json").read_text(encoding="utf-8"))
    broken: list[tuple[str, str]] = []
    seen: set[str] = set()
    for article in data["articles"]:
        for field in ("hero_image", "thumb_image"):
            url = article[field]
            if url in seen:
                continue
            seen.add(url)
            if not check_url(url):
                broken.append((article["slug"], url))
    print(f"Checked {len(seen)} unique image URLs across {len(data['articles'])} articles.")
    if broken:
        print(f"BROKEN ({len(broken)}):")
        for slug, url in broken[:30]:
            print(f"  {slug}")
            print(f"    {url}")
        return 1
    print("All image URLs OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
