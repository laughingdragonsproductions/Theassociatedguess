"""Pick hero/thumb images that match article topics via image_prompt and keywords."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from typing import Any

# Verified Unsplash photo IDs (GET-tested). Do not add IDs without running validate_images.py.
VERIFIED_PHOTO_IDS: frozenset[str] = frozenset(
    {
        "1461988320302-91bde64fc8e4",
        "1514888286974-6c03e2ca1dba",
        "1552053831-71594a27632d",
        "1548199973-03cce0bbc87b",
        "1558618666-fcd25c85cd64",
        "1558642452-9d2a7deb7f62",
        "1444464666168-49d633b86797",
        "1534438327276-14e5300c3a48",
        "1497366216548-37526070297c",
        "1552664730-d307ca884978",
        "1556761175-b413da4baf72",
        "1553877522-43269d4ea984",
        "1512941937669-90a1b58e7e9c",
        "1516321318423-f06f85e504b3",
        "1556909114-f6e7ad7d3136",
        "1503676260728-1c00da094a0b",
        "1562774053-701939374585",
        "1581091226825-a6a2a5aee158",
        "1519741497674-611481863552",
        "1518770660439-4636190af475",
        "1551288049-bebda4e38f71",
        "1460925895917-afdab827c52f",
        "1564013799919-ab600027ffc6",
        "1449824913935-59a10b8d2000",
        "1600880292203-757bb62b4baf",
        "1500530855697-b586d89ba3ee",
        "1506905925346-21bda4d32df4",
        "1586528116311-ad8dd3c8310d",
        "1504711434969-e33886168f5c",
        "1565299624946-b28f40a0ae38",
        "1635070041078-e363dbe005cb",
        "1507003211169-0a1dd7228f2d",
        "1521587760476-6c12a4b040da",
        "1541961017774-22349e4a1262",
        "1522071820081-009f0129c71c",
        "1472214103451-9374bd1c798e",
        "1504384308090-c894fdcc538d",
        "1560472354-b33ff0c44a43",
        "1582719478250-c89cae4dc85b",
        "1618005182384-a83a8bd57fbe",
        "1621905252507-b35492cc74b4",
        "1571019613454-1cb2f99b2d8b",
    }
)

FALLBACK_PHOTO = "1461988320302-91bde64fc8e4"

IMAGE_TOPICS: list[dict[str, Any]] = [
    {
        "id": "cat",
        "keywords": ["cat", "cats", "feline", "tabby", "kitten", "meow", "pancake"],
        "photos": ["1514888286974-6c03e2ca1dba"],
    },
    {
        "id": "dog",
        "keywords": ["dog", "retriever", "mayor", "dalmatian", "puppy", "canine", "spot"],
        "photos": ["1552053831-71594a27632d", "1548199973-03cce0bbc87b"],
    },
    {
        "id": "squirrel",
        "keywords": ["squirrel", "squirrels", "rodent"],
        "photos": ["1558618666-fcd25c85cd64"],
    },
    {
        "id": "hamster",
        "keywords": ["hamster", "vampire", "bakery rodent"],
        "photos": ["1565299624946-b28f40a0ae38", "1541961017774-22349e4a1262"],
    },
    {
        "id": "bee",
        "keywords": ["bee", "bees", "honey", "hive", "heist"],
        "photos": ["1558642452-9d2a7deb7f62", "1472214103451-9374bd1c798e"],
    },
    {
        "id": "butterfly",
        "keywords": ["butterfly", "butterflies", "lepidoptera"],
        "photos": ["1472214103451-9374bd1c798e", "1558618666-fcd25c85cd64"],
    },
    {
        "id": "bird",
        "keywords": ["pigeon", "pigeons", "bird", "birds"],
        "photos": ["1444464666168-49d633b86797"],
    },
    {
        "id": "fish",
        "keywords": ["fish", "tank", "aquarium", "aquatic"],
        "photos": ["1472214103451-9374bd1c798e"],
    },
    {
        "id": "ghost",
        "keywords": ["ghost", "ghosts", "haunt", "spooky", "sheet", "specter", "paranormal"],
        "photos": ["1507003211169-0a1dd7228f2d", "1618005182384-a83a8bd57fbe"],
    },
    {
        "id": "ufo",
        "keywords": ["ufo", "alien", "aliens", "nebraska", "object", "invasion", "extraterrestrial"],
        "photos": ["1618005182384-a83a8bd57fbe", "1635070041078-e363dbe005cb"],
    },
    {
        "id": "space",
        "keywords": ["space", "moon", "galactic", "planet", "orbit", "astronaut", "cosmos", "solar"],
        "photos": ["1618005182384-a83a8bd57fbe", "1635070041078-e363dbe005cb", "1506905925346-21bda4d32df4"],
    },
    {
        "id": "gym",
        "keywords": ["gym", "fitness", "membership", "workout", "running shoes", "exercise"],
        "photos": ["1534438327276-14e5300c3a48"],
    },
    {
        "id": "office",
        "keywords": ["office", "cubicle", "worker", "corporate", "hr", "exhausted", "calendar", "tasks", "break room", "crayons"],
        "photos": ["1497366216548-37526070297c", "1552664730-d307ca884978", "1522071820081-009f0129c71c"],
    },
    {
        "id": "meeting",
        "keywords": ["meeting", "conference", "whiteboard", "agenda", "email", "could have been"],
        "photos": ["1556761175-b413da4baf72", "1553877522-43269d4ea984"],
    },
    {
        "id": "phone",
        "keywords": ["phone", "smartphone", "group chat", "eclipse glasses", "headline", "pill", "news app"],
        "photos": ["1512941937669-90a1b58e7e9c", "1516321318423-f06f85e504b3"],
    },
    {
        "id": "smart_home",
        "keywords": ["alexa", "speaker", "smart speaker", "fridge", "refrigerator", "leftover", "leftovers", "kitchen counter"],
        "photos": ["1556909114-f6e7ad7d3136", "1504384308090-c894fdcc538d"],
    },
    {
        "id": "school",
        "keywords": ["school", "student", "detention", "headphones", "podcast", "teacher", "high school"],
        "photos": ["1503676260728-1c00da094a0b"],
    },
    {
        "id": "college",
        "keywords": ["college", "university", "classroom", "professor", "meme", "lecture", "campus"],
        "photos": ["1562774053-701939374585", "1503676260728-1c00da094a0b"],
    },
    {
        "id": "fire",
        "keywords": ["fire", "firefighter", "fire truck", "dalmatian vest", "fire department"],
        "photos": ["1581091226825-a6a2a5aee158", "1548199973-03cce0bbc87b"],
    },
    {
        "id": "wedding",
        "keywords": ["wedding", "bride", "groom", "marriage", "regret", "binder", "planner"],
        "photos": ["1519741497674-611481863552"],
    },
    {
        "id": "tech",
        "keywords": ["tech", "ceo", "ai", "spreadsheet", "software", "digital", "virtual", "crypto", "currency", "furniture", "pumpkin carving"],
        "photos": ["1518770660439-4636190af475", "1551288049-bebda4e38f71", "1618005182384-a83a8bd57fbe"],
    },
    {
        "id": "grocery",
        "keywords": ["grocery", "supermarket", "checkout", "store", "shopper", "pumpkin", "gourd", "gourds", "fall display"],
        "photos": ["1461988320302-91bde64fc8e4", "1565299624946-b28f40a0ae38"],
    },
    {
        "id": "government",
        "keywords": ["council", "mayor", "congress", "hearing", "election", "vote", "law", "ordinance", "city hall", "pentagon", "government"],
        "photos": ["1449824913935-59a10b8d2000", "1522071820081-009f0129c71c"],
    },
    {
        "id": "economy",
        "keywords": ["economist", "stock", "portfolio", "market", "trader", "finance", "chart", "equity", "ambivalence"],
        "photos": ["1460925895917-afdab827c52f", "1551288049-bebda4e38f71"],
    },
    {
        "id": "suburban",
        "keywords": ["neighbor", "leaf blower", "porch", "suburban", "street", "7 a.m", "leaves"],
        "photos": ["1564013799919-ab600027ffc6"],
    },
    {
        "id": "city",
        "keywords": ["crosswalk", "pedestrian", "button", "traffic", "road rage", "clipboard", "driver", "parking", "crosswalk"],
        "photos": ["1449824913935-59a10b8d2000", "1564013799919-ab600027ffc6"],
    },
    {
        "id": "health",
        "keywords": ["cdc", "fda", "drug", "pill", "health", "guidance", "grass safely", "public health", "poster"],
        "photos": ["1571019613454-1cb2f99b2d8b", "1506905925346-21bda4d32df4"],
    },
    {
        "id": "video_call",
        "keywords": ["video conference", "camera-on", "zoom", "togetherness", "grid", "remote", "webcam"],
        "photos": ["1600880292203-757bb62b4baf"],
    },
    {
        "id": "fair",
        "keywords": ["fair", "fairground", "contest", "judges", "scorecard", "overthinking", "carnival"],
        "photos": ["1500530855697-b586d89ba3ee"],
    },
    {
        "id": "museum",
        "keywords": ["museum", "exhibit", "gallery", "password", "sticky note", "kiosk"],
        "photos": ["1541961017774-22349e4a1262"],
    },
    {
        "id": "park",
        "keywords": ["national park", "trail", "hiker", "mountain", "existential", "park", "city park"],
        "photos": ["1506905925346-21bda4d32df4", "1472214103451-9374bd1c798e"],
    },
    {
        "id": "airline",
        "keywords": ["airline", "airplane", "cabin", "boarding pass", "flight", "economy", "regret"],
        "photos": ["1504384308090-c894fdcc538d", "1582719478250-c89cae4dc85b"],
    },
    {
        "id": "weather",
        "keywords": ["weather", "rain", "drizzle", "forecast", "gray sky", "cloud", "window", "coffee cup"],
        "photos": ["1507003211169-0a1dd7228f2d", "1560472354-b33ff0c44a43"],
    },
    {
        "id": "library",
        "keywords": ["library", "study room", "screaming", "acoustic", "books", "read", "reading"],
        "photos": ["1521587760476-6c12a4b040da"],
    },
    {
        "id": "delivery",
        "keywords": ["postal", "package", "delivery", "tracking", "truck", "mail", "when we get there"],
        "photos": ["1586528116311-ad8dd3c8310d"],
    },
    {
        "id": "newsroom",
        "keywords": ["newsroom", "whiteboard", "editor", "journalism", "vault", "tally", "50-article"],
        "photos": ["1504711434969-e33886168f5c", "1461988320302-91bde64fc8e4"],
    },
    {
        "id": "board_game",
        "keywords": ["board game", "rulebook", "dice", "tabletop", "players"],
        "photos": ["1522071820081-009f0129c71c", "1500530855697-b586d89ba3ee"],
    },
    {
        "id": "food",
        "keywords": ["bakery", "bread", "muffin", "sausage", "sandwich", "sushi", "food", "pastry"],
        "photos": ["1565299624946-b28f40a0ae38", "1461988320302-91bde64fc8e4"],
    },
    {
        "id": "bike",
        "keywords": ["bike", "bicycle", "space bike", "cycling"],
        "photos": ["1558618666-fcd25c85cd64", "1449824913935-59a10b8d2000"],
    },
    {
        "id": "video",
        "keywords": ["viral", "video contest", "social media", "filming"],
        "photos": ["1516321318423-f06f85e504b3", "1600880292203-757bb62b4baf"],
    },
    {
        "id": "science",
        "keywords": ["scientist", "research", "gravity", "physics", "time travel", "warming", "study", "peer-reviewed", "telescope"],
        "photos": ["1635070041078-e363dbe005cb", "1618005182384-a83a8bd57fbe"],
    },
    {
        "id": "eco",
        "keywords": ["eco-friendly", "energy", "environment", "green", "sustainable"],
        "photos": ["1472214103451-9374bd1c798e", "1506905925346-21bda4d32df4"],
    },
    {
        "id": "leprechaun",
        "keywords": ["leprechaun", "leprechauns", "irish", "gold coin"],
        "photos": ["1500530855697-b586d89ba3ee", "1621905252507-b35492cc74b4"],
    },
]

SLUG_OVERRIDES: dict[str, str] = {
    "ghost-parking": "ghost",
    "city-council-approves-new-ghost-parking-ordinance": "ghost",
    "local-bakery-introduces-new-ghost-bread": "ghost",
    "mystery-solved-why-ghosts-can-t-read-books": "library",
    "eco-friendly-ghosts": "ghost",
    "mysterious-vampire-hamster-disappears-from-local-bakery": "hamster",
    "the-great-honey-bee-heist": "bee",
    "the-curious-case-of-the-dancing-dalmatian": "dog",
    "alien-cats-invasion-alert": "cat",
    "cats-can-read-minds": "cat",
    "scientists-confirm-cats-have-been-ignoring-us-on-purpose": "cat",
    "the-case-of-the-disappearing-cats": "cat",
    "galactic-pets": "dog",
    "digital-sushi": "food",
    "alien-sausage": "food",
    "muffin-mystery": "food",
    "pentagon-confirms-area-51-contains-mostly-unread-emails": "government",
    "pentagon-says-nebraska-object-is-one-of-the-normal-ones": "ufo",
    "time-travel-causes-gravity": "science",
    "global-warming-caused-by-gravity": "science",
    "silly-scientists-discover-new-planet": "space",
    "moon-base-craze": "space",
    "galactic-tourism": "space",
    "space-bike": "bike",
    "phased-out-phones": "phone",
    "digital-pumpkin": "grocery",
    "digital-furniture": "tech",
    "digital-currency-trend": "tech",
    "virtual-reality-conference": "tech",
    "viral-video-contest": "video",
}

SECTION_DEFAULTS: dict[str, str] = {
    "Science": "science",
    "Business": "economy",
    "Politics": "government",
    "Local": "city",
    "Culture": "museum",
    "Opinion": "office",
    "Strange America": "fair",
    "News": "newsroom",
}

TOKEN_RE = re.compile(r"[a-z0-9']+")


def _unsplash(photo_id: str, width: int, height: int) -> str:
    return (
        f"https://images.unsplash.com/photo-{photo_id}"
        f"?auto=format&fit=crop&w={width}&h={height}&q=80"
    )


def _sanitize_photos(photos: list[str]) -> list[str]:
    clean = [p for p in photos if p in VERIFIED_PHOTO_IDS]
    return clean or [FALLBACK_PHOTO]


def _validate_topic_photos() -> None:
    for topic in IMAGE_TOPICS:
        topic["photos"] = _sanitize_photos(topic["photos"])
        unknown = set(topic.get("photos", [])) - VERIFIED_PHOTO_IDS
        if unknown:
            raise ValueError(f"Topic {topic['id']} has unverified photos: {unknown}")


_validate_topic_photos()


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def _topic_by_id(topic_id: str) -> dict[str, Any] | None:
    for topic in IMAGE_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None


def _pick_photo(topic: dict[str, Any], seed: str) -> str:
    photos = _sanitize_photos(topic["photos"])
    idx = sum(ord(c) for c in seed) % len(photos)
    return photos[idx]


def _score_topic(topic: dict[str, Any], prompt_text: str, body_text: str) -> int:
    prompt_tokens = _tokens(prompt_text)
    body_tokens = _tokens(body_text)
    score = 0
    for kw in topic["keywords"]:
        parts = kw.split()
        if len(parts) > 1:
            if kw in prompt_text.lower():
                score += 6
            elif kw in body_text.lower():
                score += 3
            continue
        if kw in prompt_tokens:
            score += 4
        if kw in body_tokens:
            score += 2
    return score


def photo_url_reachable(url: str, timeout: float = 12.0) -> bool:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status < 400
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def pick_article_images(
    *,
    article_id: str,
    slug: str,
    title: str,
    dek: str,
    section: str,
    body: str,
    image_prompt: str = "",
) -> tuple[str, str]:
    """Return (hero_url, thumb_url) best matching the article concept."""
    if image_prompt.startswith("http://") or image_prompt.startswith("https://"):
        return image_prompt, image_prompt

    override_id = SLUG_OVERRIDES.get(slug)
    if override_id:
        topic = _topic_by_id(override_id)
        if topic:
            photo = _pick_photo(topic, article_id or slug)
            return _unsplash(photo, 800, 500), _unsplash(photo, 400, 300)

    search_blob = " ".join(
        [
            image_prompt,
            title,
            dek,
            slug.replace("-", " "),
            body[:600],
        ]
    )
    best_topic: dict[str, Any] | None = None
    best_score = 0
    for topic in IMAGE_TOPICS:
        score = _score_topic(topic, image_prompt or search_blob, search_blob)
        if score > best_score:
            best_score = score
            best_topic = topic

    if best_topic is None or best_score == 0:
        fallback_id = SECTION_DEFAULTS.get(section, "newsroom")
        best_topic = _topic_by_id(fallback_id) or IMAGE_TOPICS[0]

    photo = _pick_photo(best_topic, article_id or slug)
    return _unsplash(photo, 800, 500), _unsplash(photo, 400, 300)
