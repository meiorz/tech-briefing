from types import SimpleNamespace

from briefing.fetchers import rss
from briefing.models import Feed

FEED = Feed("test", "Test", "security", "https://example.com/feed")
XML = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>t</title>
<item><title> First </title><link>https://example.com/1</link>
<description>&lt;p&gt;Hello &amp;amp; &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;</description>
<pubDate>Fri, 02 Oct 2026 14:30:00 GMT</pubDate></item>
<item><title>No link</title></item>
</channel></rss>"""


def test_summary_strips_tags_and_entities():
    assert rss._summary({"summary": "<p>A &amp;  <b>B</b></p>"}) == "A & B"


def test_summary_truncates_at_word_boundary():
    text = rss._summary({"summary": "word " * 200}, max_len=22)
    assert text == "word word word word…"


def test_fetch_feed_populates_summary(monkeypatch):
    monkeypatch.setattr(rss, "get", lambda url: SimpleNamespace(content=XML))
    items = rss.fetch_feed(FEED)
    assert len(items) == 1                       # entry without a link is skipped
    item = items[0]
    assert item.title == "First"
    assert item.summary == "Hello & world"
    assert item.published.isoformat() == "2026-10-02T14:30:00+00:00"


def test_fetch_all_survives_a_failing_feed(monkeypatch):
    def fake_get(url):
        if "bad" in url:
            raise ConnectionError("boom")
        return SimpleNamespace(content=XML)
    monkeypatch.setattr(rss, "get", fake_get)
    bad = Feed("bad", "Bad", "security", "https://bad.example/feed")
    assert [i.source for i in rss.fetch_all([bad, FEED])] == ["test"]


ATOM = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>t</title>
<entry><title>Atom</title><link href="https://example.com/atom"/>
<updated>2026-10-01T08:00:00Z</updated></entry>
<entry><title>Undated</title><link href="https://example.com/undated"/></entry>
</feed>"""


def test_published_falls_back_to_updated_and_none(monkeypatch):
    monkeypatch.setattr(rss, "get", lambda url: SimpleNamespace(content=ATOM))
    dated, undated = rss.fetch_feed(FEED)
    assert dated.published.isoformat() == "2026-10-01T08:00:00+00:00"
    assert undated.published is None


def test_non_feed_response_is_logged(monkeypatch, caplog):
    page = b"<html><body><h1>Just a moment...</h1><p>Checking your browser"
    monkeypatch.setattr(rss, "get", lambda url: SimpleNamespace(content=page))
    assert rss.fetch_feed(FEED) == []
    assert "no parseable entries" in caplog.text
