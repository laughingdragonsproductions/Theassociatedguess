#!/usr/bin/env py -3
"""Check internal links in the built static site."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

SITE = Path(__file__).resolve().parents[1]
HREF_RE = re.compile(r"""href=["']([^"'#?]+)""", re.I)


def resolve_href(page: Path, href: str) -> Path | None:
    href = href.strip()
    if not href or href.startswith(("http://", "https://", "mailto:")):
        return None
    target = (page.parent / href).resolve()
    try:
        target.relative_to(SITE.resolve())
    except ValueError:
        return None
    if target.is_dir():
        return target / "index.html"
    return target


def main() -> int:
    pages = list(SITE.rglob("*.html"))
    broken: list[tuple[str, str]] = []
    checked = 0
    for page in pages:
        if "scripts" in page.parts:
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        for href in HREF_RE.findall(text):
            href = unquote(href.strip())
            if href.endswith((".css", ".js")):
                target = resolve_href(page, href)
            else:
                target = resolve_href(page, href)
            if target is None:
                continue
            checked += 1
            if not target.exists():
                rel = page.relative_to(SITE)
                broken.append((str(rel), href))
    print(f"Checked {checked} internal links across {len(pages)} pages.")
    if broken:
        print(f"BROKEN ({len(broken)}):")
        for page, href in broken[:50]:
            print(f"  {page} -> {href}")
        return 1
    print("All internal links OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
