from types import SimpleNamespace

from briefing.fetchers import hn

STORIES = {
    1: {"id": 1, "type": "story", "title": "Good", "url": "https://a.example", "score": 150, "time": 1790000000},
    2: {"id": 2, "type": "story", "title": "Low", "score": 5, "time": 1790000000},
    3: {"id": 3, "type": "story", "deleted": True, "score": 500},
    4: {"id": 4, "type": "job", "title": "Hiring", "score": 500, "time": 1790000000},
    5: {"id": 5, "type": "story", "score": 500},                       # no title/time
    6: {"id": 6, "type": "story", "title": "Ask HN", "score": 200, "time": 1790000000},
}


def fake_get(url):
    if url.endswith("topstories.json"):
        return SimpleNamespace(json=lambda: list(STORIES))
    story_id = int(url.rsplit("/", 1)[1].split(".")[0])
    return SimpleNamespace(json=lambda: STORIES[story_id])


def test_fetch_top_filters_and_skips_malformed(monkeypatch):
    monkeypatch.setattr(hn, "get", fake_get)
    items = hn.fetch_top()
    assert [i.title for i in items] == ["Good", "Ask HN"]
    assert items[1].url == "https://news.ycombinator.com/item?id=6"


def test_fetch_top_returns_empty_when_hn_is_down(monkeypatch):
    def down(url):
        raise ConnectionError("down")
    monkeypatch.setattr(hn, "get", down)
    assert hn.fetch_top() == []
