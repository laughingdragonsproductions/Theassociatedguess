"""Pick hero/thumb images that match article topics via image_prompt and keywords."""

from __future__ import annotations

import re
from typing import Any

# Unsplash photo IDs (license-free). Multiple variants per topic for variety.
IMAGE_TOPICS: list[dict[str, Any]] = [
    {
        "id": "cat",
        "keywords": ["cat", "cats", "feline", "tabby", "kitten", "meow", "pancake"],
        "photos": ["1514888286974-6c03e2ca1dba", "1574158622682-6b3884f9f2a1", "1495360012281-59ab365573e7"],
    },
    {
        "id": "dog",
        "keywords": ["dog", "retriever", "mayor", "dalmatian", "puppy", "canine", "spot"],
        "photos": ["1552053831-71594a27632d", "1548199973-03cce0bbc87b", "1587300003388-59208fb9627d"],
    },
    {
        "id": "squirrel",
        "keywords": ["squirrel", "squirrels", "rodent"],
        "photos": ["1425087651642-229b496b4956", "1558618666-fcd25c85cd64"],
    },
    {
        "id": "hamster",
        "keywords": ["hamster", "vampire", "bakery rodent"],
        "photos": ["1548767797-daf760e35424", "1509440154316-774875420890"],
    },
    {
        "id": "bee",
        "keywords": ["bee", "bees", "honey", "hive", "heist"],
        "photos": ["1558642452-9d2a7deb7f62", "1587049359896-3eaa5bca0f63"],
    },
    {
        "id": "butterfly",
        "keywords": ["butterfly", "butterflies", "lepidoptera"],
        "photos": ["1452574810820-3364f33ef134", "1526333289474-3d1146c939a7"],
    },
    {
        "id": "bird",
        "keywords": ["pigeon", "pigeons", "bird", "birds"],
        "photos": ["1552728087-52d9acf1ba96", "1444464666168-49d633b86797"],
    },
    {
        "id": "fish",
        "keywords": ["fish", "tank", "aquarium", "aquatic"],
        "photos": ["1522069169874-58c6837614e6", "1544551761-7873614b3403"],
    },
    {
        "id": "ghost",
        "keywords": ["ghost", "ghosts", "haunt", "spooky", "sheet", "specter", "paranormal"],
        "photos": ["1509249900867-e780eee44f7a", "1518709268805-4e9042f9a960", "1516975086484-de6f8668ba56"],
    },
    {
        "id": "ufo",
        "keywords": ["ufo", "alien", "aliens", "nebraska", "object", "invasion", "extraterrestrial"],
        "photos": ["1419242901074-263e57524453", "1446776877081-d282765f29e0", "1454789548928-9efa44db849e"],
    },
    {
        "id": "space",
        "keywords": ["space", "moon", "galactic", "planet", "orbit", "astronaut", "cosmos", "solar"],
        "photos": ["1446776653964-39c2d0770fea", "1454789548928-9efa44db849e", "1419242901074-263e57524453"],
    },
    {
        "id": "gym",
        "keywords": ["gym", "fitness", "membership", "workout", "running shoes", "exercise"],
        "photos": ["1534438327276-14e5300c3a48", "1571902940602-82c3b3810016"],
    },
    {
        "id": "office",
        "keywords": ["office", "cubicle", "worker", "corporate", "hr", "exhausted", "calendar", "tasks", "break room", "crayons"],
        "photos": ["1497366216548-37526070297c", "1552664730-d307ca884978", "1484486569610-79e06ccb259f"],
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
        "photos": ["1556909114-f6e7ad7d3136", "1556911221-bff31c812dba"],
    },
    {
        "id": "school",
        "keywords": ["school", "student", "detention", "headphones", "podcast", "teacher", "high school"],
        "photos": ["1503676260728-1c00da094a0b", "1523050855928-8d8e4d2456f8"],
    },
    {
        "id": "college",
        "keywords": ["college", "university", "classroom", "professor", "meme", "lecture", "campus"],
        "photos": ["1523050855928-8d8e4d2456f8", "1562774053-701939374585"],
    },
    {
        "id": "fire",
        "keywords": ["fire", "firefighter", "fire truck", "dalmatian vest", "fire department"],
        "photos": ["1545558017881-5d0f4a0706b3", "1581091226825-a6a2a5aee158"],
    },
    {
        "id": "wedding",
        "keywords": ["wedding", "bride", "groom", "marriage", "regret", "binder", "planner"],
        "photos": ["1519741497674-611481863552", "1465497426033-626f29ec474f"],
    },
    {
        "id": "tech",
        "keywords": ["tech", "ceo", "ai", "spreadsheet", "software", "digital", "virtual", "crypto", "currency", "furniture", "pumpkin carving"],
        "photos": ["1518770660439-4636190af475", "1551288049-bebda4e38f71", "1592478841-608e4683a849"],
    },
    {
        "id": "grocery",
        "keywords": ["grocery", "supermarket", "checkout", "store", "shopper", "pumpkin", "gourd", "gourds", "fall display"],
        "photos": ["1578916170965-d72f4c299e36", "1509042237870-99d41d685e73"],
    },
    {
        "id": "government",
        "keywords": ["council", "mayor", "congress", "hearing", "election", "vote", "law", "ordinance", "city hall", "pentagon", "government"],
        "photos": ["1541873673006-4e322d87a781", "1559825498-0368e0f12623"],
    },
    {
        "id": "economy",
        "keywords": ["economist", "stock", "portfolio", "market", "trader", "finance", "chart", "equity", "ambivalence"],
        "photos": ["1611974789855-9c98a795bf08", "1460925895917-afdab827c52f"],
    },
    {
        "id": "suburban",
        "keywords": ["neighbor", "leaf blower", "porch", "suburban", "street", "7 a.m", "leaves"],
        "photos": ["1564013799919-ab600027ffc6", "1449848741920-346efe7e407a"],
    },
    {
        "id": "city",
        "keywords": ["crosswalk", "pedestrian", "button", "traffic", "road rage", "clipboard", "driver", "parking", "crosswalk"],
        "photos": ["1449824913935-59a10b8d2000", "1449965406639-454133f5a0f5", "1519005035164-e7a7443ef573"],
    },
    {
        "id": "health",
        "keywords": ["cdc", "fda", "drug", "pill", "health", "guidance", "grass safely", "public health", "poster"],
        "photos": ["1576091160399-112ba8d25d1f", "1558907353-1953d9338f55"],
    },
    {
        "id": "video_call",
        "keywords": ["video conference", "camera-on", "zoom", "togetherness", "grid", "remote", "webcam"],
        "photos": ["1600880292203-757bb62b4baf", "1588196749597-9bc252f87de2"],
    },
    {
        "id": "fair",
        "keywords": ["fair", "fairground", "contest", "judges", "scorecard", "overthinking", "carnival"],
        "photos": ["1566576919021-49a5497e8d11", "1500530855697-b586d89ba3ee"],
    },
    {
        "id": "museum",
        "keywords": ["museum", "exhibit", "gallery", "password", "sticky note", "kiosk"],
        "photos": ["1568665797760-0813f7a96991", "1518998053901-7c588e83d962"],
    },
    {
        "id": "park",
        "keywords": ["national park", "trail", "hiker", "mountain", "existential", "park", "city park"],
        "photos": ["1506905925346-21bda4d32df4", "1464822759023-fed6222852fc"],
    },
    {
        "id": "airline",
        "keywords": ["airline", "airplane", "cabin", "boarding pass", "flight", "economy", "regret"],
        "photos": ["1436491862712-8296e69db914", "1583608205776-dfd35f0c9ab5"],
    },
    {
        "id": "weather",
        "keywords": ["weather", "rain", "drizzle", "forecast", "gray sky", "cloud", "window", "coffee cup"],
        "photos": ["1515694342877-7d8c67f5c9b9", "1428908728789-a62ee3840689"],
    },
    {
        "id": "library",
        "keywords": ["library", "study room", "screaming", "acoustic", "books", "read", "reading"],
        "photos": ["1481627834876-b78344385afd", "1507842217343-583154707686"],
    },
    {
        "id": "delivery",
        "keywords": ["postal", "package", "delivery", "tracking", "truck", "mail", "when we get there"],
        "photos": ["1566576721346-7c0a8c8b4937", "1586528116311-ad8dd3c8310d"],
    },
    {
        "id": "newsroom",
        "keywords": ["newsroom", "whiteboard", "editor", "journalism", "vault", "tally", "50-article"],
        "photos": ["1504711434969-e33886168f5c", "1495026682319-66bb9ca0c4e2"],
    },
    {
        "id": "board_game",
        "keywords": ["board game", "rulebook", "dice", "tabletop", "players"],
        "photos": ["1611375854745-5b8a41e4e149", "1606166188517-6a103050ea16"],
    },
    {
        "id": "food",
        "keywords": ["bakery", "bread", "muffin", "sausage", "sandwich", "sushi", "food", "pastry"],
        "photos": ["1509440154316-774875420890", "1579584425559-d4725e0b88f2", "1565299624946-b28f40a0ae38"],
    },
    {
        "id": "bike",
        "keywords": ["bike", "bicycle", "space bike", "cycling"],
        "photos": ["1571333250630-f0230c146854", "1485968579580-b5d5502c4f67"],
    },
    {
        "id": "video",
        "keywords": ["viral", "video contest", "social media", "filming"],
        "photos": ["1492691527719-9d1e07e534b6", "1611162616475-46b635cb6848"],
    },
    {
        "id": "science",
        "keywords": ["scientist", "research", "gravity", "physics", "time travel", "warming", "study", "peer-reviewed", "telescope"],
        "photos": ["153209434978-654e1123e9c7", "1635070041078-e363dbe005cb", "1446774269880-aa4c194e726a"],
    },
    {
        "id": "eco",
        "keywords": ["eco-friendly", "energy", "environment", "green", "sustainable"],
        "photos": ["1473341304170-fd89c7bc2ded", "1542601906990-b4e3ba7a8f08"],
    },
    {
        "id": "leprechaun",
        "keywords": ["leprechaun", "leprechauns", "irish", "gold coin"],
        "photos": ["1516975086484-de6f8668ba56", "1558618666-fcd25c85cd64"],
    },
]

# Hard overrides for titles/slugs where keyword scoring still misfires.
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


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


def _topic_by_id(topic_id: str) -> dict[str, Any] | None:
    for topic in IMAGE_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None


def _pick_photo(topic: dict[str, Any], seed: str) -> str:
    photos = topic["photos"]
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
    custom_hero = ""
    custom_thumb = ""
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
    hero = custom_hero or _unsplash(photo, 800, 500)
    thumb = custom_thumb or _unsplash(photo, 400, 300)
    return hero, thumb
