import calendar
import html
import logging
import re
from datetime import datetime, timezone

import feedparser

from briefing.http import get
from briefing.models import Feed, Item

TAG = re.compile(r"<[^>]+>")

log = logging.getLogger(__name__)

def _published(entry) -> datetime | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc) if t else None

def _summary(entry, max_len: int = 400) -> str:
    text = html.unescape(TAG.sub(" ", entry.get("summary", "")))
    text = " ".join(text.split())                                 # collapse whitespace
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"                 # cut at a word boundary

def fetch_feed(feed: Feed, limit: int = 10) -> list[Item]:
    resp = get(feed.url)
    parsed = feedparser.parse(resp.content)
    if parsed.bozo and not parsed.entries:      # e.g. a 200 bot-challenge HTML page
        log.warning("Feed %s returned no parseable entries: %s", feed.id, parsed.get("bozo_exception"))
    return [
        Item(feed.id, feed.category, e.title.strip(), e.link, _published(e), _summary(e))
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
