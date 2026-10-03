import calendar
import logging
from datetime import datetime, timezone

import feedparser
import requests

from briefing.models import Feed, Item

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "tech-briefing/0.1 (personal digest)"}

def _published(entry) -> datetime | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc) if t else None

def fetch_feed(feed: Feed, limit: int = 10) -> list[Item]:
    resp = requests.get(feed.url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    return [
        Item(feed.id, feed.category, e.title.strip(), e.link, _published(e))
        for e in parsed.entries[:limit]
        if e.get("title") and e.get("link")
    ]

def fetch_all(feeds: list[Feed], limit: int = 10) -> list[Item]:
    items: list[Item] = []
    for feed in feeds:
        try:
            items.extend(fetch_feed(feed, limit))
        except Exception as exc:
            log.warning("Feed %s failed: %s", feed.id, exc)
    return items

if __name__ == "__main__":
    from collections import Counter
    from briefing.sources import RSS_FEEDS

    logging.basicConfig(level=logging.INFO)
    results = fetch_all(RSS_FEEDS)
    for source, n in Counter(i.source for i in results).items():
        print(f"{source:15} {n}")