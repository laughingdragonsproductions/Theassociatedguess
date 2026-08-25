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
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

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
BACKLOG = ARTICLES_DIR / "Backlog"
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
ADSENSE_PUBLISHER = "ca-pub-7048606415692002"
CONTACT_EMAIL = "laughingdragonsproductions@gmail.com"
LEGAL_NAME = "Laughing Dragons Productions"
PARENT_SITE = "https://laughing-dragons.com"
TIPS_EMAIL = f"tips@{DOMAIN}"

ABOUT_HTML = """
<p class="about-lede">The Associated Guess was founded on a conviction we have never apologized for: the country deserves hard-hitting journalism - clear-eyed, unsentimental, and unwilling to trade accuracy for access.</p>
<p>We studied the major outlets closely. We attended the briefings, read the earnings calls, and noted how often “breaking” meant “gently confirmed by a person who would not be quoted.” We concluded that if we wanted reporting that actually landed, we would have to pursue it the old-fashioned way: assign the story, verify the details, and publish before the world had a chance to contradict us by happening differently.</p>
<p>Our newsroom does not run on tips from unnamed officials, leaked slide decks, or the slow accident of events. We run on editors who ask hard questions, correspondents who file from places that sound plausible, and a standards desk that treats every dateline as a promise. When a source speaks on the record, they are on the record. When we describe a policy, a protest, or a squirrel-related municipal ordinance, we describe it with the gravity it deserves.</p>
<p>We are independent. We are obsessive about craft. We believe the reader should finish an article slightly more informed and significantly more concerned than when they started - whether the subject is the economy, the climate, or the behavioral standards now expected of smart refrigerators.</p>
<p>If something on our front page strikes you as unlikely, read it again. Read the quotes. Follow the logic. We trust you to draw your own conclusions. We have already drawn ours.</p>
<p class="about-signature"><em>SERIOUS NEWS. ABSURD WORLD.</em>  -  The Editors</p>
<section class="about-real">
  <h2>Who publishes this</h2>
  <p><strong>The Associated Guess</strong> is a satirical news property operated by <strong>{legal}</strong>, an independent media and maker studio. This site is part of the Laughing Dragons portfolio alongside games, tools, podcasts, and shop projects hosted at <a href="{parent}" rel="noopener">{parent_host}</a>.</p>
  <p>Every headline here is fictional parody  -  written in deadpan news style, not reported as fact. We publish new stories daily. For tips, corrections, or rights questions, see our <a href="contact.html">Contact</a> page.</p>
  <h2>More from Laughing Dragons</h2>
  <ul>
    <li><a href="{parent}" rel="noopener">Laughing Dragons Productions</a>  -  studio hub (games, kids show, tools, shop)</li>
    <li><a href="https://chittinandchattin.com" rel="noopener">Chittin &amp; Chattin</a>  -  podcast</li>
    <li><a href="{parent}/contact/" rel="noopener">Studio contact form</a>  -  general inquiries across the portfolio</li>
  </ul>
  <p>Publisher email: <a href="mailto:{email}">{email}</a></p>
</section>
""".format(
    legal=LEGAL_NAME,
    parent=PARENT_SITE,
    parent_host=PARENT_SITE.replace("https://", ""),
    email=CONTACT_EMAIL,
)

CONTACT_HTML = """
<p>Reach the newsroom or the studio behind this site. <strong>The Associated Guess</strong> is published by <strong>{legal}</strong> (<a href="{parent}" rel="noopener">laughing-dragons.com</a>).</p>
<h2>Newsroom tips</h2>
<p>Story ideas, absurd local ordinances, and satire corrections: <a href="mailto:{tips}">{tips}</a> (routes to our studio inbox).</p>
<h2>General inquiries</h2>
<p><strong>{legal}</strong><br />
Email: <a href="mailto:{email}">{email}</a><br />
Studio hub: <a href="{parent}" rel="noopener">{parent_host}</a></p>
<h2>What we can help with</h2>
<ul>
  <li>Corrections or attribution on a satire piece</li>
  <li>Reprint and licensing questions</li>
  <li>Site, privacy, or advertising issues</li>
  <li>Other Laughing Dragons projects  -  games, podcast, shop, kids show</li>
</ul>
<p>For non-news studio mail, you may also use the <a href="{parent}/contact/" rel="noopener">Laughing Dragons contact form</a>.</p>
""".format(
    legal=LEGAL_NAME,
    parent=PARENT_SITE,
    parent_host=PARENT_SITE.replace("https://", ""),
    tips=TIPS_EMAIL,
    email=CONTACT_EMAIL,
)

PRIVACY_HTML = """
<p><strong>Last updated:</strong> August 22, 2026</p>
<p><strong>The Associated Guess</strong> is published by <strong>{legal}</strong> ("we," "us") at {domain}. This policy describes how we handle information when you visit the site. Our umbrella studio site is <a href="{parent}" rel="noopener">laughing-dragons.com</a>.</p>
<h2>Information we collect</h2>
<ul>
  <li><strong>Server and analytics logs</strong>  -  IP address, browser type, pages viewed, and referrers collected by our host (GitHub Pages / Cloudflare).</li>
  <li><strong>Contact email</strong>  -  if you email us, we receive your address and message contents.</li>
  <li><strong>Cookies</strong>  -  set by Google AdSense and our hosting/CDN partners (see Advertising).</li>
</ul>
<h2>Advertising</h2>
<p>We may show Google AdSense display ads in the site header and footer on editorial pages, and one display unit below the hero image on article pages. We do not place ad units inside article body text, sidebars, legal pages (privacy, terms), or empty search results.</p>
<p>Google AdSense may use cookies to serve ads based on your prior visits to this or other websites. Google's use of advertising cookies enables it and its partners to serve ads based on visits to our site and/or other sites on the Internet.</p>
<p>You may opt out of personalized advertising via <a href="https://adssettings.google.com" rel="noopener">Google Ads Settings</a> or <a href="https://www.aboutads.info" rel="noopener">www.aboutads.info</a>.</p>
<h2>Third-party services</h2>
<ul>
  <li><strong>Google AdSense</strong>  -  advertising (shared publisher account across Laughing Dragons portfolio sites)</li>
  <li><strong>Cloudflare / GitHub Pages</strong>  -  hosting and delivery</li>
  <li><strong>Google Fonts</strong>  -  typography (may log IP)</li>
  <li><strong>Unsplash</strong>  -  editorial stock imagery linked from article pages</li>
</ul>
<h2>Contact</h2>
<p>Questions: <a href="mailto:{email}">{email}</a> · Studio: <a href="{parent}/contact/" rel="noopener">{parent_host}/contact/</a></p>
""".format(
    legal=LEGAL_NAME,
    domain=DOMAIN,
    parent=PARENT_SITE,
    parent_host=PARENT_SITE.replace("https://", ""),
    email=CONTACT_EMAIL,
)

TERMS_HTML = """
<p><strong>Last updated:</strong> August 22, 2026</p>
<p><strong>The Associated Guess</strong> ({domain}) is a satirical news publication operated by <strong>{legal}</strong>. Stories are fictional parody and should not be read as factual reporting.</p>
<h2>Use of the site</h2>
<p>You may read and share links to our articles for personal, non-commercial use. Do not scrape, republish full articles, or misrepresent satire as real news.</p>
<h2>Advertising</h2>
<p>Third-party ads (including Google AdSense) may appear on some pages. We are not responsible for advertiser content. Do not click ads to artificially inflate revenue.</p>
<h2>Disclaimer</h2>
<p>All characters, quotes, and events described are invented unless explicitly labeled otherwise. No professional, legal, medical, or financial advice is offered.</p>
<h2>Related sites</h2>
<p>Other properties under {legal} include <a href="{parent}" rel="noopener">laughing-dragons.com</a> and linked portfolio sites. Each has its own terms where posted.</p>
<h2>Contact</h2>
<p><a href="mailto:{email}">{email}</a></p>
""".format(
    legal=LEGAL_NAME,
    domain=DOMAIN,
    parent=PARENT_SITE,
    email=CONTACT_EMAIL,
)


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
    if "{nnnn}" in name or "{slug}" in name:
        return True
    if any(skip in name for skip in SKIP_NAME_PARTS):
        return True
    return False


def collect_vault_paths(*, include_date_folders: bool = False) -> list[Path]:
    """Stories-Used only by default; date-folder drafts stay off the live site until ON004 publishes."""
    paths: list[Path] = []
    if not ARTICLES_DIR.is_dir():
        return paths
    if STORIES_USED.is_dir():
        paths.extend(sorted(STORIES_USED.glob("*.md")))
    if include_date_folders:
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


def normalize_dashes(text: str) -> str:
    return text.replace("\u2014", " - ")


def find_pending_backlog_articles() -> list[Path]:
    if not BACKLOG.is_dir():
        return []
    return [
        p
        for p in sorted(BACKLOG.glob("*.md"))
        if not is_excluded_path(p) and p.name.lower() != "readme.md"
    ]


def find_pending_date_folder_articles() -> list[Path]:
    pending: list[tuple[str, str, Path]] = []
    if not ARTICLES_DIR.is_dir():
        return []
    for child in sorted(ARTICLES_DIR.iterdir()):
        if not child.is_dir() or not DATE_FOLDER_RE.match(child.name):
            continue
        for path in sorted(child.glob("*.md")):
            if is_excluded_path(path):
                continue
            pending.append((child.name, path.name.lower(), path))
    pending.sort(key=lambda row: (row[0], row[1]))
    return [path for _, _, path in pending]


def find_pending_publish_articles() -> list[Path]:
    """FIFO: Backlog first, then date-folder drafts (Carol's daily vault)."""
    backlog = find_pending_backlog_articles()
    if backlog:
        return backlog
    return find_pending_date_folder_articles()


def update_frontmatter_published(path: Path, pub_date: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("---"):
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        return
    fm = parts[1]
    if re.search(r"^published:\s*", fm, re.MULTILINE):
        fm = re.sub(r"^published:\s*.*$", f"published: {pub_date}", fm, flags=re.MULTILINE)
    else:
        fm = fm.rstrip() + f"\npublished: {pub_date}\n"
    path.write_text(f"---{fm}---{parts[2]}", encoding="utf-8")


def publish_one_pending(live_date: date | None = None) -> dict[str, Any]:
    """Move one vault draft to Stories-Used with today's live published date (ON004)."""
    live = live_date or datetime.now(ET).date()
    pub_str = live.isoformat()
    pending = find_pending_publish_articles()
    if not pending:
        return {"published": None, "live_date": pub_str, "reason": "no pending drafts in Backlog or date folders"}
    src = pending[0]
    source_queue = "Backlog" if BACKLOG in src.parents else src.parent.name
    update_frontmatter_published(src, pub_str)
    STORIES_USED.mkdir(parents=True, exist_ok=True)
    dest = STORIES_USED / src.name
    if dest.exists():
        return {"published": src.name, "live_date": pub_str, "source": source_queue, "error": "already in Stories-Used"}
    shutil.move(str(src), str(dest))
    manifest: list[dict[str, str]] = []
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = []
    manifest.append(
        {
            "id": article_id(parse_frontmatter(dest.read_text(encoding="utf-8")), dest),
            "filename": src.name,
            "from": str(src),
            "archived_at": datetime.now(UTC).isoformat(),
            "live_date": pub_str,
            "source_queue": source_queue,
        }
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"published": src.name, "live_date": pub_str, "source": source_queue, "dest": str(dest)}


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
    body = normalize_dashes(extract_body(text))
    title = normalize_dashes(extract_title(meta, body, path))
    slug = slug_from_path(path)
    if not title or len(body) < 80:
        return None
    if is_junk_article(title, body, slug):
        return None
    aid = article_id(meta, path)
    words = len(re.findall(r"\w+", body))
    read_minutes = max(1, round(words / 200))
    section = normalize_section(meta.get("section") or meta.get("category") or "News")
    dek = normalize_dashes((meta.get("dek") or "").strip() or title[:120])
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
        "byline": normalize_dashes((meta.get("byline") or "Staff").strip()),
        "dateline": normalize_dashes((meta.get("dateline") or "").strip()),
        "kind": (meta.get("kind") or "news").strip(),
        "promo": (meta.get("promo") or "none").strip(),
        "promo_url": (meta.get("promo_url") or "").strip(),
        "body": body,
        "body_html": body_to_html(body, slug=slug),
        "read_minutes": read_minutes,
        "source_path": str(path),
        "hero_image": hero_image,
        "thumb_image": thumb_image,
        "image_prompt": image_prompt,
        "published": (meta.get("published") or "").strip(),
        "_num_id": numeric_id(aid),
    }


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

HOUSE_ADS: list[dict[str, str]] = [
    {
        "id": "hub",
        "title": "Laughing Dragons Productions",
        "line": "Games, tools, podcasts, and the studio behind this paper.",
        "url": "https://laughing-dragons.com",
        "cta": "Visit hub",
    },
    {
        "id": "chittin",
        "title": "Chittin and Chattin",
        "line": "A podcast about nothing in particular and everything at once.",
        "url": "https://chittinandchattin.com",
        "cta": "Listen now",
    },
    {
        "id": "them1947",
        "title": "THEM 1947",
        "line": "Display-grade alien Grey prints and classified-adjacent files.",
        "url": "https://them1947.com",
        "cta": "Browse archive",
    },
    {
        "id": "litprintz",
        "title": "Lit Printz",
        "line": "Drinkware, wellness theater, and things printed different.",
        "url": "https://litprintz.com",
        "cta": "Shop prints",
    },
]

HOUSE_AD_EVERY = 3
MAX_HOUSE_ADS = 4


def pick_house_ad(slot: int, slug: str) -> dict[str, str]:
    seed = sum(ord(c) for c in (slug or "story")) + slot * 31
    return HOUSE_ADS[seed % len(HOUSE_ADS)]


def house_ad_markup(slot: int, slug: str) -> str:
    ad = pick_house_ad(slot, slug)
    return (
        f'<aside class="house-ad-block" aria-label="Promoted: {escape(ad["title"])}">'
        f'<span class="house-ad-label">Promoted</span>'
        f'<a class="house-ad-link" href="{html.escape(ad["url"], quote=True)}" rel="noopener sponsored">'
        f'<span class="house-ad-title">{escape(ad["title"])}</span>'
        f'<span class="house-ad-line">{escape(ad["line"])}</span>'
        f'<span class="house-ad-cta">{escape(ad["cta"])} ›</span>'
        f"</a></aside>"
    )


def inline_markdown(text: str) -> str:
    """Convert [label](url) to anchor tags; escape other text."""
    parts: list[str] = []
    last = 0
    for match in LINK_RE.finditer(text):
        if match.start() > last:
            parts.append(escape(text[last : match.start()]))
        label = escape(match.group(1))
        url = html.escape(match.group(2).strip(), quote=True)
        parts.append(f'<a href="{url}" rel="noopener">{label}</a>')
        last = match.end()
    if last < len(text):
        parts.append(escape(text[last:]))
    return "".join(parts) if parts else escape(text)


def body_to_html(body: str, slug: str = "") -> str:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]
    parts: list[str] = []
    para_count = 0
    house_count = 0
    for block in blocks:
        if block.startswith("## "):
            parts.append(f'<h2 class="article-subhead">{escape(block[3:].strip())}</h2>')
            continue
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if lines and all(ln.startswith("- ") for ln in lines):
            items = "".join(f"<li>{inline_markdown(ln[2:])}</li>" for ln in lines)
            parts.append(f"<ul class=\"article-list\">{items}</ul>")
            continue
        if block.startswith("#"):
            continue
        parts.append(f"<p>{inline_markdown(block)}</p>")
        para_count += 1
        if (
            para_count >= 2
            and para_count % HOUSE_AD_EVERY == 0
            and house_count < MAX_HOUSE_ADS
        ):
            house_count += 1
            parts.append(house_ad_markup(house_count, slug))
    return "\n".join(parts) if parts else f"<p>{escape(body[:500])}</p>"


def assign_display_dates(articles: list[dict[str, Any]]) -> None:
    dated: list[dict[str, Any]] = []
    undated: list[dict[str, Any]] = []
    for article in articles:
        pub = (article.get("published") or "").strip()
        try:
            if pub and len(pub) >= 10:
                d = date.fromisoformat(pub[:10])
                article["display_date"] = d.isoformat()
                article["display_date_long"] = format_long_date(d)
                dated.append(article)
                continue
        except ValueError:
            pass
        undated.append(article)

    undated.sort(key=lambda a: a["_num_id"] or 99999)
    start = date(2026, 1, 2)
    end = date(2026, 8, 19)
    total_days = (end - start).days
    n = len(undated)
    if n == 1:
        undated[0]["display_date"] = end.isoformat()
        undated[0]["display_date_long"] = format_long_date(end)
    elif n > 1:
        for i, article in enumerate(undated):
            offset = round(i * total_days / (n - 1))
            d = start + timedelta(days=offset)
            article["display_date"] = d.isoformat()
            article["display_date_long"] = format_long_date(d)

    articles.clear()
    articles.extend(dated + undated)
    articles.sort(key=lambda a: a["display_date"], reverse=True)


def format_long_date(d: date) -> str:
    return d.strftime("%A, %B %d, %Y").replace(" 0", " ")


def promo_footer(article: dict[str, Any]) -> str:
    promo = article.get("promo", "none")
    url = article.get("promo_url", "")
    if promo == "none" or not url:
        return ""
    return f'<p class="promo-link"><a href="{escape(url)}" rel="noopener">{escape(promo)}</a></p>'


def ad_slot_markup(key: str, extra_class: str = "") -> str:
    cls = f"ad-slot {extra_class}".strip()
    return f'<div class="{cls}" data-ad-slot="{escape(key)}"></div>'


def chrome_head(page_title: str, depth: int = 0, description: str = "", canonical_path: str = "") -> str:
    title = escape(page_title)
    meta_desc = escape(description or TAGLINE)
    root_attr = site_href("", depth).rstrip("/") or "."
    css = site_href("assets/css/paper.css", depth)
    canonical = ""
    if canonical_path:
        canonical = f'  <link rel="canonical" href="https://{DOMAIN}/{canonical_path.lstrip("/")}" />\n'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{meta_desc}" />
  <title>{title}  -  {escape(BRAND)}</title>
{canonical}  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{css}" />
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUBLISHER}" crossorigin="anonymous"></script>
</head>
<body data-site-root="{root_attr}">"""


def chrome_header(active_section: str = "", depth: int = 0, on_homepage: bool = False, show_ads: bool = True) -> str:
    today = datetime.now().strftime("%A, %B %d, %Y").replace(" 0", " ")
    home = site_href("index.html", depth)
    nav_items = "".join(
        f'<a href="{home_anchor(s.lower().replace(" ", "-"), depth, on_homepage)}" class="nav-link{" active" if s == active_section else ""}">{escape(s)}</a>'
        for s in SECTIONS
    )
    header_ad = ad_slot_markup("header", "ad-slot-header") if show_ads else ""
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
    <form class="search-box" action="{site_href("search.html", depth)}" method="get" role="search">
      <input type="search" name="q" placeholder="Search" aria-label="Search stories" autocomplete="off" />
    </form>
  </div>
  <nav class="main-nav" aria-label="Sections">
    {nav_items}
    <button type="button" class="nav-toggle" aria-label="Menu">☰</button>
  </nav>
</header>
{header_ad}"""


def chrome_footer(depth: int = 0, on_homepage: bool = False, show_ads: bool = True) -> str:
    section_links = "".join(
        f'<li><a href="{home_anchor(s.lower().replace(" ", "-"), depth, on_homepage)}">{escape(s)}</a></li>'
        for s in SECTIONS
    )
    js = site_href("assets/js/paper.js", depth)
    config_js = site_href("assets/js/config.js", depth)
    adsense_js = site_href("assets/js/adsense.js", depth)
    footer_ad = ad_slot_markup("footer", "ad-slot-footer") if show_ads else ""
    return f"""
<footer class="site-footer">
  <div class="footer-grid">
    <div>
      <strong>{escape(BRAND)}</strong>
      <p class="footer-tagline">{escape(TAGLINE)}</p>
      <p class="footer-parent">A <a href="{PARENT_SITE}" rel="noopener">{escape(LEGAL_NAME)}</a> property</p>
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
        <li><a href="{site_href("privacy.html", depth)}">Privacy</a></li>
        <li><a href="{site_href("terms.html", depth)}">Terms</a></li>
        <li><a href="{home_anchor("newsletter", depth, on_homepage)}">Newsletter</a></li>
        <li><a href="{PARENT_SITE}" rel="noopener">{escape(LEGAL_NAME)}</a></li>
      </ul>
    </div>
  </div>
  {footer_ad}
</footer>
<script src="{config_js}"></script>
<script src="{adsense_js}"></script>
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
        [article_catalog_entry(a) for a in articles],
        ensure_ascii=False,
    )

    return (
        chrome_head(
            "Home",
            description=f"Satirical news from {BRAND}  -  published by {LEGAL_NAME}. {TAGLINE}",
            canonical_path="",
        )
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
          <li>East Millfield Neighbor Association  -  leaf blower détente talks continue.</li>
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
    {ad_slot_markup("inContent", "ad-slot-in-content")}
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


def article_catalog_entry(article: dict[str, Any]) -> dict[str, Any]:
    entry = {k: v for k, v in article.items() if k not in ("body", "body_html", "source_path", "kind")}
    entry["search_text"] = " ".join(
        [
            article.get("title") or "",
            article.get("dek") or "",
            article.get("section") or "",
            article.get("byline") or "",
            article.get("dateline") or "",
            article.get("slug", "").replace("-", " "),
            (article.get("body") or "")[:500],
        ]
    )
    return entry


def write_static_pages() -> None:
    pages = [
        (
            "about.html",
            "About",
            ABOUT_HTML,
            f"About {BRAND}  -  satirical news published by {LEGAL_NAME}. Portfolio hub: laughing-dragons.com.",
            "about.html",
        ),
        (
            "contact.html",
            "Contact",
            CONTACT_HTML,
            f"Contact {BRAND} and {LEGAL_NAME}  -  tips, corrections, and studio inquiries.",
            "contact.html",
        ),
        (
            "privacy.html",
            "Privacy Policy",
            PRIVACY_HTML,
            f"Privacy policy for {BRAND}, operated by {LEGAL_NAME}.",
            "privacy.html",
        ),
        (
            "terms.html",
            "Terms of Service",
            TERMS_HTML,
            f"Terms of service for {BRAND} satirical news.",
            "terms.html",
        ),
    ]
    for name, title, body, description, canonical in pages:
        path = SITE / name
        show_ads = name not in {"privacy.html", "terms.html"}
        path.write_text(
            chrome_head(title, description=description, canonical_path=canonical)
            + chrome_header(on_homepage=False, show_ads=show_ads)
            + f"<main class='page-static'><h1>{escape(title)}</h1>{body}</main>"
            + chrome_footer(on_homepage=False, show_ads=show_ads),
            encoding="utf-8",
        )
    search_path = SITE / "search.html"
    search_path.write_text(
        chrome_head(
            "Search",
            description=f"Search the {BRAND} archive of satirical news stories.",
            canonical_path="search.html",
        )
        + chrome_header(on_homepage=False, show_ads=False)
        + """
<main class="page-search">
  <header class="search-page-header">
    <h1>Search</h1>
    <p class="search-page-lede">Find stories across The Associated Guess archive.</p>
  </header>
  <div id="search-status" class="search-status" role="status" aria-live="polite"></div>
  <ol id="search-results" class="search-results"></ol>
</main>
"""
        + chrome_footer(on_homepage=False, show_ads=False),
        encoding="utf-8",
    )


def write_robots_txt() -> None:
    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: https://{DOMAIN}/sitemap.xml\n",
        encoding="utf-8",
    )


def write_sitemap(articles: list[dict[str, Any]]) -> None:
    urls = [
        f"https://{DOMAIN}/",
        f"https://{DOMAIN}/about.html",
        f"https://{DOMAIN}/contact.html",
        f"https://{DOMAIN}/privacy.html",
        f"https://{DOMAIN}/terms.html",
        f"https://{DOMAIN}/search.html",
    ]
    for article in articles:
        urls.append(f"https://{DOMAIN}/article/{article['slug']}/")
    body = '<?xml version="1.0" encoding="UTF-8"?>\n'
    body += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        body += f"  <url><loc>{escape(url)}</loc></url>\n"
    body += "</urlset>\n"
    (SITE / "sitemap.xml").write_text(body, encoding="utf-8")


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


def build_site(archive: bool = False, publish_one: bool = False) -> dict[str, Any]:
    published_one: dict[str, Any] | None = None
    if publish_one:
        published_one = publish_one_pending()
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
    catalog = [article_catalog_entry(a) for a in ingested]
    (SITE / "data" / "articles.json").write_text(
        json.dumps({"brand": BRAND, "articles": catalog}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (SITE / "index.html").write_text(generate_index(ingested), encoding="utf-8")
    (SITE / "CNAME").write_text(f"{DOMAIN}\n", encoding="utf-8")
    write_static_pages()
    write_robots_txt()
    write_sitemap(ingested)
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

    return {
        "articles": len(ingested),
        "archived": moved,
        "paths_scanned": len(paths),
        "published_one": published_one,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build The Associated Guess site from vault")
    parser.add_argument("--archive-used", action="store_true", help="Bulk-move all date-folder files to Stories-Used (legacy)")
    parser.add_argument(
        "--publish-one",
        action="store_true",
        help="Publish one pending vault draft with today's live ET date (ON004 default)",
    )
    args = parser.parse_args()
    if args.archive_used and args.publish_one:
        parser.error("Use --publish-one OR --archive-used, not both")
    result = build_site(archive=args.archive_used, publish_one=args.publish_one)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
