#!/usr/bin/env python3
"""Find articles sharing the same hero image and log headlines for bulk art work."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DESKTOP_AGENT = Path(r"G:\LocalAIagent\desktop-agent")
if str(DESKTOP_AGENT) not in sys.path:
    sys.path.insert(0, str(DESKTOP_AGENT))

from scripts.article_images import HERO_ASSETS_DIR  # noqa: E402
from scripts.build_from_vault import (  # noqa: E402
    collect_vault_paths,
    ingest_article,
)

DEFAULT_REPORT_MD = Path(r"G:\openclaw\business\satire-news\alerts\duplicate-images-report.md")
DEFAULT_REPORT_JSON = Path(r"G:\openclaw\business\satire-news\alerts\duplicate-images-report.json")
DEFAULT_REPORT_CSV = Path(r"G:\openclaw\business\satire-news\alerts\duplicate-images-bulk-art.csv")
PENDING_HERO_PHOTO = "1512941937669-90a1b58e7e9c"

UNSPLASH_RE = re.compile(r"photo-([\d]+-[0-9a-f]+)", re.I)
ASSET_RE = re.compile(r"/assets/images/([^/?#]+)", re.I)


def normalize_image_key(hero_url: str) -> str:
    url = (hero_url or "").strip()
    if not url:
        return "empty"
    match = UNSPLASH_RE.search(url)
    if match:
        return f"unsplash:{match.group(1).lower()}"
    match = ASSET_RE.search(url)
    if match:
        return f"asset:{match.group(1).lower()}"
    return url.split("?")[0].lower()


def image_label(image_key: str) -> str:
    if image_key.startswith("unsplash:"):
        return f"Unsplash {image_key.split(':', 1)[1]}"
    if image_key.startswith("asset:"):
        return f"Local asset {image_key.split(':', 1)[1]}"
    return image_key


def file_sha256(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest()


def scan_binary_duplicate_assets() -> dict[str, list[str]]:
    """Same PNG bytes saved under different filenames."""
    by_hash: dict[str, list[str]] = defaultdict(list)
    if not HERO_ASSETS_DIR.is_dir():
        return {}
    for path in sorted(HERO_ASSETS_DIR.glob("*.png")):
        digest = file_sha256(path)
        if digest:
            by_hash[digest].append(path.name)
    return {digest: names for digest, names in by_hash.items() if len(names) > 1}


def collect_articles(*, include_drafts: bool) -> list[dict[str, Any]]:
    paths = collect_vault_paths(include_date_folders=include_drafts)
    articles: list[dict[str, Any]] = []
    seen_slugs: set[str] = set()
    for path in paths:
        article = ingest_article(path)
        if not article:
            continue
        slug = str(article.get("slug") or "")
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        articles.append(article)
    return articles


def build_duplicate_report(articles: list[dict[str, Any]]) -> dict[str, Any]:
    by_image: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for article in articles:
        hero = str(article.get("hero_image") or "")
        key = normalize_image_key(hero)
        by_image[key].append(
            {
                "slug": article.get("slug"),
                "title": article.get("title"),
                "dek": article.get("dek"),
                "section": article.get("section"),
                "published": article.get("published"),
                "image_prompt": article.get("image_prompt"),
                "hero_image": hero,
                "source_path": article.get("source_path"),
            }
        )

    duplicate_groups = []
    for key, rows in sorted(by_image.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(rows) < 2:
            continue
        duplicate_groups.append(
            {
                "image_key": key,
                "image_label": image_label(key),
                "sample_hero_url": rows[0].get("hero_image"),
                "count": len(rows),
                "articles": sorted(rows, key=lambda r: str(r.get("title") or "")),
            }
        )

    binary_dupes = [
        {"sha256": digest, "filenames": names}
        for digest, names in scan_binary_duplicate_assets().items()
    ]

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "article_count": len(articles),
        "unique_images": len(by_image),
        "duplicate_image_groups": len(duplicate_groups),
        "articles_sharing_a_duplicate": sum(g["count"] for g in duplicate_groups),
        "binary_asset_duplicates": binary_dupes,
        "groups": duplicate_groups,
    }


def render_bulk_art_csv(report: dict[str, Any]) -> str:
    """One row per article that shares a duplicate hero — for bulk image generation."""
    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "slug",
            "title",
            "dek",
            "section",
            "published",
            "image_prompt",
            "current_image_key",
            "needs_unique_hero",
        ]
    )
    for group in report.get("groups") or []:
        key = str(group.get("image_key") or "")
        for row in group.get("articles") or []:
            writer.writerow(
                [
                    row.get("slug") or "",
                    row.get("title") or "",
                    row.get("dek") or "",
                    row.get("section") or "",
                    row.get("published") or "",
                    row.get("image_prompt") or "",
                    key,
                    "yes",
                ]
            )
    return buffer.getvalue()


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# The Associated Guess — duplicate hero images",
        "",
        f"- Generated: {report.get('generated_at', '')}",
        f"- Articles scanned: {report.get('article_count', 0)}",
        f"- Unique hero images: {report.get('unique_images', 0)}",
        f"- Duplicate image groups: {report.get('duplicate_image_groups', 0)}",
        f"- Articles in a duplicate group: {report.get('articles_sharing_a_duplicate', 0)}",
        "",
        "Use this list to generate unique hero art in bulk. Each group shares the same resolved hero image.",
        "",
    ]

    binary = report.get("binary_asset_duplicates") or []
    if binary:
        lines.extend(["## Identical PNG files (different filenames)", ""])
        for row in binary:
            lines.append(f"- `{', '.join(row['filenames'])}`")
        lines.append("")

    lines.append("## Duplicate hero groups")
    lines.append("")
    for group in report.get("groups") or []:
        lines.extend(
            [
                f"### {group['image_label']} — {group['count']} articles",
                "",
                f"- Image key: `{group['image_key']}`",
                f"- Sample URL: {group.get('sample_hero_url', '')}",
                "",
                "| Headline | Slug | Published | image_prompt |",
                "|----------|------|-----------|--------------|",
            ]
        )
        for row in group.get("articles") or []:
            title = str(row.get("title") or "").replace("|", "\\|")
            slug = str(row.get("slug") or "")
            published = str(row.get("published") or "")
            prompt = str(row.get("image_prompt") or "").replace("|", "\\|")[:120]
            lines.append(f"| {title} | `{slug}` | {published} | {prompt} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit duplicate hero images across vault articles")
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Include date-folder drafts, not just Stories-Used",
    )
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--csv", type=Path, default=DEFAULT_REPORT_CSV)
    args = parser.parse_args()

    articles = collect_articles(include_drafts=args.include_drafts)
    report = build_duplicate_report(articles)

    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.markdown.write_text(render_markdown(report), encoding="utf-8")
    args.csv.write_text(render_bulk_art_csv(report), encoding="utf-8")

    placeholder_count = 0
    for group in report.get("groups") or []:
        if PENDING_HERO_PHOTO in str(group.get("image_key") or ""):
            placeholder_count = int(group.get("count") or 0)
            break

    print(json.dumps({
        "articles": report["article_count"],
        "duplicate_groups": report["duplicate_image_groups"],
        "articles_in_duplicates": report["articles_sharing_a_duplicate"],
        "pending_placeholder_articles": placeholder_count,
        "markdown": str(args.markdown),
        "json": str(args.json),
        "csv": str(args.csv),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
