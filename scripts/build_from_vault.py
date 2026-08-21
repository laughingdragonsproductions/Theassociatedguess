#!/usr/bin/env py -3
"""Build The Associated Guess static site from the satire vault."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DESKTOP_AGENT = Path(r"G:\LocalAIagent\desktop-agent")
if str(DESKTOP_AGENT) not in sys.path:
    sys.path.insert(0, str(DESKTOP_AGENT))

from integrations.satire_vault_monitor import ID_RE, parse_frontmatter  # noqa: E402

from article_images import pick_article_images  # noqa: E402

VAULT = Path(r"G:\openclaw\business\satire-news")
SITE = ROOT
ARTICLES_DIR = VAULT / "articles"
STORIES_USED = ARTICLES_DIR / "Stories-Used"
MANIFEST_PATH = STORIES_USED / "manifest.json"
DATE_FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SKIP_NAME_PARTS = ("example-article", "manifest.json", "satire-article")
SECTIONS = [
    "News",
    "Politics",
    "Business",
    "Science",
    "Culture",
    "Local",
    "Opinion",
    "Strange America",
]
BRAND = "The Associated Guess"
TAGLINE = "SERIOUS NEWS. ABSURD WORLD."
DOMAIN = "theassociatedguess.com"

ABOUT_HTML = """
<p class="about-lede">The Associated Guess was founded on a conviction we have never apologized for: the country deserves hard-hitting journalism—clear-eyed, unsentimental, and unwilling to trade accuracy for access.</p>
<p>We studied the major outlets closely. We attended the briefings, read the earnings calls, and noted how often “breaking” meant “gently confirmed by a person who would not be quoted.” We concluded that if we wanted reporting that actually landed, we would have to pursue it the old-fashioned way: assign the story, verify the details, and publish before the world had a chance to contradict us by happening differently.</p>
<p>Our newsroom does not run on tips from unnamed officials, leaked slide decks, or the slow accident of events. We run on editors who ask hard questions, correspondents who file from places that sound plausible, and a standards desk that treats every dateline as a promise. When a source speaks on the record, they are on the record. When we describe a policy, a protest, or a squirrel-related municipal ordinance, we describe it with the gravity it deserves.</p>
<p>We are independent. We are obsessive about craft. We believe the reader should finish an article slightly more informed and significantly more concerned than when they started—whether the subject is the economy, the climate, or the behavioral standards now expected of smart refrigerators.</p>
<p>If something on our front page strikes you as unlikely, read it again. Read the quotes. Follow the logic. We trust you to draw your own conclusions. We have already drawn ours.</p>
<p class="about-signature"><em>SERIOUS NEWS. ABSURD WORLD.</em> — The Editors</p>
"""


def site_href(path: str, depth: int = 0) -> str:
    """Relative URL from a page at the given depth (0 = site root)."""
    clean = path.lstrip("/")
    if depth <= 0:
        return clean
    return ("../" * depth) + clean


def escape(text: str) -> str:
    return html.escape(text or "", quote=True)


def article_href(slug: str, depth: int = 0) -> str:
    if depth <= 0:
        return f"article/{slug}/"
    return f"../{slug}/"


def home_anchor(fragment: str, depth: int = 0, on_homepage: bool = False) -> str:
    tag = fragment.lstrip("#")
    if on_homepage:
        return f"#{tag}"
    return f"{site_href('index.html', depth)}#{tag}"


def extract_body(text: str) -> str:
    stripped = text.lstrip("\ufeff")
    if stripped.startswith("---"):
        parts = stripped.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return stripped.strip()


def extract_title(meta: dict[str, str], body: str, path: Path) -> str:
    title = (meta.get("title") or "").strip()
    if title:
        return title
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    stem = path.stem
    if stem.startswith("dr-"):
        parts = stem.split("-", 2)
        if len(parts) >= 3:
            return parts[2].replace("-", " ").title()
    return stem.replace("-", " ").title()


def slug_from_path(path: Path) -> str:
    stem = path.stem
    raw = stem
    if stem.startswith("dr-"):
        match = re.match(r"dr-\d+-(.+)", stem, re.I)
        if match:
            raw = match.group(1)
    return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-") or "story"


def article_id(meta: dict[str, str], path: Path) -> str:
    raw = (meta.get("id") or path.stem).strip()
    match = ID_RE.search(raw)
    if match:
        return f"dr-{int(match.group(1)):04d}"
    return raw


def numeric_id(article_id_str: str) -> int:
    match = ID_RE.search(article_id_str)
    return int(match.group(1)) if match else 0


def is_excluded_path(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    if "quarantine" in parts:
        return True
    name = path.name.lower()
    if name == "manifest.json":
        return True
    if any(skip in name for skip in SKIP_NAME_PARTS):
        return True
    return False


def collect_vault_paths() -> list[Path]:
    paths: list[Path] = []
    if not ARTICLES_DIR.is_dir():
        return paths
    if STORIES_USED.is_dir():
        paths.extend(sorted(STORIES_USED.glob("*.md")))
    for child in sorted(ARTICLES_DIR.iterdir()):
        if not child.is_dir():
            continue
        if child.name in ("Stories-Used", "quarantine"):
            continue
        if DATE_FOLDER_RE.match(child.name):
            paths.extend(sorted(child.glob("*.md")))
    unique: dict[str, Path] = {}
    for path in paths:
        if is_excluded_path(path):
            continue
        key = path.name.lower()
        if key not in unique:
            unique[key] = path
    return sorted(unique.values(), key=lambda p: p.name.lower())


def normalize_section(raw: str) -> str:
    section = (raw or "News").strip()
    if section.lower() == "satire":
        return "News"
    for name in SECTIONS:
        if section.lower() == name.lower():
            return name
    return "News"


def is_junk_article(title: str, body: str, slug: str) -> bool:
    if re.search(r"\bsatire\b", title, re.I):
        return True
    if "satire-article" in slug.lower():
        return True
    sentences = len(re.findall(r"[.!?]", body))
    if sentences < 2:
        return True
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if len(lines) >= 4 and sentences < len(lines) // 2:
        return True
    return False


def ingest_article(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    meta = parse_frontmatter(text)
    body = extract_body(text)
    title = extract_title(meta, body, path)
    slug = slug_from_path(path)
    if not title or len(body) < 80:
        return None
    if is_junk_article(title, body, slug):
        return None
    aid = article_id(meta, path)
    words = len(re.findall(r"\w+", body))
    read_minutes = max(1, round(words / 200))
    section = normalize_section(meta.get("section") or meta.get("category") or "News")
    dek = (meta.get("dek") or "").strip() or title[:120]
    if re.search(r"\bsatire\b", dek, re.I):
        dek = title[:120]
    image_prompt = (meta.get("image_prompt") or "").strip()
    hero_image, thumb_image = pick_article_images(
        article_id=aid,
        slug=slug,
        title=title,
        dek=dek,
        section=section,
        body=body,
        image_prompt=image_prompt,
    )
    return {
        "id": aid,
        "slug": slug,
        "title": title,
        "dek": dek,
        "section": section,
        "byline": (meta.get("byline") or "Staff").strip(),
        "dateline": (meta.get("dateline") or "").strip(),
        "kind": (meta.get("kind") or "news").strip(),
        "promo": (meta.get("promo") or "none").strip(),
        "promo_url": (meta.get("promo_url") or "").strip(),
        "body": body,
        "body_html": body_to_html(body),
        "read_minutes": read_minutes,
        "source_path": str(path),
        "hero_image": hero_image,
        "thumb_image": thumb_image,
        "image_prompt": image_prompt,
        "_num_id": numeric_id(aid),
    }


def body_to_html(body: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    parts: list[str] = []
    for para in paragraphs:
        if para.startswith("#"):
            continue
        parts.append(f"<p>{escape(para)}</p>")
    return "\n".join(parts) if parts else f"<p>{escape(body[:500])}</p>"


def assign_display_dates(articles: list[dict[str, Any]]) -> None:
    articles.sort(key=lambda a: a["_num_id"] or 99999)
    start = date(2026, 1, 2)
    end = date(2026, 8, 19)
    total_days = (end - start).days
    n = len(articles)
    if n <= 1:
        if articles:
            articles[0]["display_date"] = end.isoformat()
            articles[0]["display_date_long"] = format_long_date(end)
        return
    for i, article in enumerate(articles):
        offset = round(i * total_days / (n - 1))
        d = start + timedelta(days=offset)
        article["display_date"] = d.isoformat()
        article["display_date_long"] = format_long_date(d)
    articles.sort(key=lambda a: a["display_date"], reverse=True)


def format_long_date(d: date) -> str:
    return d.strftime("%A, %B %d, %Y").replace(" 0", " ")


def promo_footer(article: dict[str, Any]) -> str:
    promo = article.get("promo", "none")
    url = article.get("promo_url", "")
    if promo == "none" or not url:
        return ""
    return f'<p class="promo-link"><a href="{escape(url)}" rel="noopener">{escape(promo)}</a></p>'


def chrome_head(page_title: str, depth: int = 0) -> str:
    title = escape(page_title)
    root_attr = site_href("", depth).rstrip("/") or "."
    css = site_href("assets/css/paper.css", depth)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{escape(TAGLINE)}" />
  <title>{title} — {escape(BRAND)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{css}" />
</head>
<body data-site-root="{root_attr}">"""


def chrome_header(active_section: str = "", depth: int = 0, on_homepage: bool = False) -> str:
    today = datetime.now().strftime("%A, %B %d, %Y").replace(" 0", " ")
    home = site_href("index.html", depth)
    nav_items = "".join(
        f'<a href="{home_anchor(s.lower().replace(" ", "-"), depth, on_homepage)}" class="nav-link{" active" if s == active_section else ""}">{escape(s)}</a>'
        for s in SECTIONS
    )
    return f"""
<header class="site-header">
  <div class="utility-bar">
    <span class="utility-date">{today}</span>
    <nav class="utility-links">
      <a href="{site_href("about.html", depth)}">About</a>
      <a href="{site_href("contact.html", depth)}">Contact</a>
      <a href="{home_anchor("newsletter", depth, on_homepage)}">Newsletter</a>
      <span class="subscribe-cta" data-feature="subscription" aria-hidden="true"><a href="#">Subscribe</a></span>
      <a href="#">Sign In</a>
    </nav>
  </div>
  <div class="masthead-row">
    <div class="weather-widget">72°F · Partly Absurd · Millfield</div>
    <div class="masthead-center">
      <a href="{home}" class="masthead-logo">{escape(BRAND)}</a>
      <p class="masthead-tagline">{escape(TAGLINE)}</p>
    </div>
    <form class="search-box" action="#" onsubmit="return false;">
      <input type="search" placeholder="Search" aria-label="Search" />
    </form>
  </div>
  <nav class="main-nav" aria-label="Sections">
    {nav_items}
    <button type="button" class="nav-toggle" aria-label="Menu">☰</button>
  </nav>
</header>"""


def chrome_footer(depth: int = 0, on_homepage: bool = False) -> str:
    section_links = "".join(
        f'<li><a href="{home_anchor(s.lower().replace(" ", "-"), depth, on_homepage)}">{escape(s)}</a></li>'
        for s in SECTIONS
    )
    js = site_href("assets/js/paper.js", depth)
    return f"""
<footer class="site-footer">
  <div class="footer-grid">
    <div>
      <strong>{escape(BRAND)}</strong>
      <p class="footer-tagline">{escape(TAGLINE)}</p>
      <p class="footer-copy">© 2026 {escape(BRAND)} · {escape(DOMAIN)}</p>
    </div>
    <div>
      <h4>Sections</h4>
      <ul>{section_links}</ul>
    </div>
    <div>
      <h4>Company</h4>
      <ul>
        <li><a href="{site_href("about.html", depth)}">About</a></li>
        <li><a href="{site_href("contact.html", depth)}">Contact</a></li>
        <li><a href="{home_anchor("newsletter", depth, on_homepage)}">Newsletter</a></li>
      </ul>
    </div>
  </div>
</footer>
<script src="{js}"></script>
</body>
</html>"""


def render_card(article: dict[str, Any], size: str = "small", depth: int = 0) -> str:
    url = article_href(article["slug"], depth)
    return f"""
<article class="story-card story-card-{size}">
  <a href="{url}" class="story-thumb-link">
    <img src="{escape(article['thumb_image'])}" alt="" loading="lazy" class="story-thumb" />
  </a>
  <p class="story-kicker">{escape(article['section'].upper())}</p>
  <h3 class="story-headline"><a href="{url}">{escape(article['title'])}</a></h3>
  <p class="story-dek">{escape(article['dek'][:140])}</p>
  <p class="story-meta">By {escape(article['byline'])} · {escape(article['display_date_long'])} · {article['read_minutes']} min read</p>
</article>"""


def render_trending_list(articles: list[dict[str, Any]], limit: int = 5, depth: int = 0) -> str:
    items = []
    for i, a in enumerate(articles[:limit], 1):
        url = article_href(a["slug"], depth)
        items.append(
            f'<li><span class="trend-rank">{i}</span> '
            f'<a href="{url}">{escape(a["title"])}</a></li>'
        )
    return "\n".join(items)


def render_archive(articles: list[dict[str, Any]], depth: int = 0) -> str:
    by_month: dict[str, list[dict[str, Any]]] = {}
    for a in articles:
        d = date.fromisoformat(a["display_date"])
        key = d.strftime("%B %Y")
        by_month.setdefault(key, []).append(a)
    chunks = []
    for month in sorted(by_month.keys(), key=lambda m: datetime.strptime(m, "%B %Y"), reverse=True):
        rows = []
        for a in by_month[month]:
            url = article_href(a["slug"], depth)
            rows.append(
                f'<li><a href="{url}">{escape(a["title"])}</a> '
                f'<span class="archive-meta">{escape(a["display_date_long"])} · {escape(a["section"])}</span></li>'
            )
        chunks.append(f'<section class="archive-month"><h3>{escape(month)}</h3><ul>{"".join(rows)}</ul></section>')
    return "\n".join(chunks)


def generate_index(articles: list[dict[str, Any]]) -> str:
    secondary = articles[4:8]
    section_blocks = []
    for section in SECTIONS:
        sec_articles = [a for a in articles if a["section"] == section][:5]
        if not sec_articles:
            continue
        cards = "".join(render_card(a, depth=0) for a in sec_articles)
        sid = section.lower().replace(" ", "-")
        section_blocks.append(
            f'<section class="section-rail" id="{sid}"><h2 class="section-title">{escape(section)}</h2><div class="card-grid">{cards}</div></section>'
        )
    opinion = [a for a in articles if a["section"] == "Opinion"][:4]
    investigations = [a for a in articles if "invest" in a["title"].lower() or a["section"] == "Strange America"][:4]
    if not opinion:
        opinion = articles[8:12]
    if not investigations:
        investigations = articles[12:16]

    catalog_json = json.dumps(
        [{k: v for k, v in a.items() if k not in ("body", "body_html", "source_path", "kind")} for a in articles],
        ensure_ascii=False,
    )

    return (
        chrome_head("Home")
        + chrome_header(on_homepage=True)
        + f"""
<main class="page-home">
  <div class="home-top">
    <div class="home-main">
      <section class="fold-random" aria-label="Top stories">
        <div id="fold-hero" class="fold-hero shell"></div>
        <div id="fold-grid" class="fold-grid shell"></div>
      </section>
      <section class="secondary-grid">
        <h2 class="visually-hidden">More headlines</h2>
        <div class="card-grid four-up">
          {"".join(render_card(a, depth=0) for a in secondary)}
        </div>
      </section>
      {"".join(section_blocks)}
      <section class="opinion-block" id="opinion">
        <h2 class="section-title">Opinion &amp; Investigations</h2>
        <div class="two-col">
          <div><h3>Opinion</h3>{"".join(render_card(a, "compact", depth=0) for a in opinion[:2])}</div>
          <div><h3>Investigations</h3>{"".join(render_card(a, "compact", depth=0) for a in investigations[:2])}</div>
        </div>
      </section>
      <section class="community-notices">
        <h2 class="section-title">Community Notices</h2>
        <ul>
          <li>East Millfield Neighbor Association — leaf blower détente talks continue.</li>
          <li>Library Scream Booth now accepts appointments through December.</li>
          <li>City crosswalk placebo buttons rated "surprisingly satisfying" in customer survey.</li>
        </ul>
      </section>
      <section class="long-archive" id="news">
        <h2 class="section-title">Archive</h2>
        {render_archive(articles, depth=0)}
      </section>
    </div>
    <aside class="home-sidebar">
      <section class="trending-box">
        <div class="tab-bar">
          <button type="button" class="tab active" data-tab="trending">Trending</button>
          <button type="button" class="tab" data-tab="mostread">Most Read</button>
          <button type="button" class="tab" data-tab="latest">Latest</button>
        </div>
        <ol class="trending-list" data-panel="trending"></ol>
        <ol class="trending-list hidden" data-panel="mostread"></ol>
        <ol class="trending-list hidden" data-panel="latest"></ol>
      </section>
      <section class="newsletter-box" id="newsletter">
        <h3>The Guess Brief</h3>
        <p>Daily absurdity. Zero refunds.</p>
        <form action="#" onsubmit="return false;">
          <input type="email" placeholder="Email address" aria-label="Email" />
          <button type="submit">Sign Up</button>
        </form>
        <p class="subscribe-cta newsletter-subscribe-note" data-feature="subscription" aria-hidden="true">Paid subscription coming soon.</p>
      </section>
    </aside>
  </div>
</main>
<script type="application/json" id="articles-data">{catalog_json}</script>
"""
        + chrome_footer(0, on_homepage=True)
    )


def generate_article_page(article: dict[str, Any]) -> str:
    depth = 2
    return (
        chrome_head(article["title"], depth)
        + chrome_header(article["section"], depth, on_homepage=False)
        + f"""
<main class="page-article">
  <article class="full-article">
    <p class="story-kicker">{escape(article['section'].upper())}</p>
    <h1 class="article-title">{escape(article['title'])}</h1>
    <p class="article-dek">{escape(article['dek'])}</p>
    <p class="article-meta">By {escape(article['byline'])} · {escape(article['display_date_long'])} · {article['read_minutes']} min read</p>
    <figure class="article-hero">
      <img src="{escape(article['hero_image'])}" alt="" />
    </figure>
    <div class="article-body">
      {article['body_html']}
      {promo_footer(article)}
    </div>
    <p class="back-link"><a href="{site_href("index.html", depth)}">← Back to front page</a></p>
  </article>
</main>
"""
        + chrome_footer(depth, on_homepage=False)
    )


def write_static_pages() -> None:
    for name, title, body in [
        ("about.html", "About", ABOUT_HTML),
        ("contact.html", "Contact", "<p>tips@theassociatedguess.com · Millfield, probably.</p>"),
    ]:
        path = SITE / name
        path.write_text(
            chrome_head(title) + chrome_header(on_homepage=False) + f"<main class='page-static'><h1>{escape(title)}</h1>{body}</main>" + chrome_footer(on_homepage=False),
            encoding="utf-8",
        )


def archive_used(ingested: list[dict[str, Any]]) -> int:
    STORIES_USED.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str]] = []
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = []
    moved = 0
    now = datetime.now(UTC).isoformat()
    for article in ingested:
        src = Path(article["source_path"])
        if STORIES_USED in src.parents or not src.exists():
            continue
        if not DATE_FOLDER_RE.match(src.parent.name):
            continue
        dest = STORIES_USED / src.name
        if dest.exists():
            continue
        shutil.move(str(src), str(dest))
        manifest.append(
            {
                "id": article["id"],
                "filename": src.name,
                "from": str(src),
                "archived_at": now,
            }
        )
        article["source_path"] = str(dest)
        moved += 1
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return moved


def build_site(archive: bool = False) -> dict[str, Any]:
    paths = collect_vault_paths()
    ingested: list[dict[str, Any]] = []
    for path in paths:
        article = ingest_article(path)
        if article:
            ingested.append(article)
    assign_display_dates(ingested)
    for a in ingested:
        a.pop("_num_id", None)

    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "article").mkdir(parents=True, exist_ok=True)
    catalog = [
        {k: v for k, v in a.items() if k not in ("body", "body_html", "source_path", "kind")}
        for a in ingested
    ]
    (SITE / "data" / "articles.json").write_text(
        json.dumps({"brand": BRAND, "articles": catalog}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (SITE / "index.html").write_text(generate_index(ingested), encoding="utf-8")
    (SITE / "CNAME").write_text(f"{DOMAIN}\n", encoding="utf-8")
    write_static_pages()
    for article in ingested:
        adir = SITE / "article" / article["slug"]
        adir.mkdir(parents=True, exist_ok=True)
        (adir / "index.html").write_text(generate_article_page(article), encoding="utf-8")

    active_slugs = {a["slug"] for a in ingested}
    article_root = SITE / "article"
    if article_root.is_dir():
        for child in article_root.iterdir():
            if child.is_dir() and child.name not in active_slugs:
                shutil.rmtree(child)

    moved = 0
    if archive:
        moved = archive_used(ingested)

    return {"articles": len(ingested), "archived": moved, "paths_scanned": len(paths)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build The Associated Guess site from vault")
    parser.add_argument("--archive-used", action="store_true", help="Move ingested date-folder files to Stories-Used")
    args = parser.parse_args()
    result = build_site(archive=args.archive_used)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
