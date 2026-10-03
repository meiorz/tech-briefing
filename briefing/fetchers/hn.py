import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from briefing.http import get
from briefing.models import Item

log = logging.getLogger(__name__)
API = "https://hacker-news.firebaseio.com/v0"


def _story(story_id: int) -> dict | None:
    try:
        return get(f"{API}/item/{story_id}.json").json()
    except Exception as exc:
        log.warning("HN item %s failled %s", story_id, exc)
        return None


def _to_item(s: dict) -> Item:
    url = s.get("url") or f"https://news.ycombinator.com/item?id={s['id']}"
    published = datetime.fromtimestamp(s["time"], tz=timezone.utc)
    return Item("hn", "tech", s["title"], url, published)


def fetch_top(limit: int = 30, min_score: int = 100) -> list[Item]:
    ids = get(f"{API}/topstories.json").json()[:limit]
    with ThreadPoolExecutor(max_workers=9) as pool:
        stories = list(pool.map(_story,ids))
        return [
            _to_item(s)
            for s in stories
            if s
            and s.get("type") == "story"
            and not s.get("deleted")
            and s.get("score", 0) >= min_score
        ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    for item in fetch_top():
        print(f"{item.published:%m-%d %H:%M} {item.title}")

