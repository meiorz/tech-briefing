from datetime import date, datetime, timezone

from briefing.models import Item
from briefing.render import render_html, render_text

DAY = date(2026, 10, 3)


def item(title="T", url="https://example.com/a", category="tech", published=None, summary=""):
    return Item("src", category, title, url, published, summary)


def test_html_escapes_title_url_and_summary():
    html = render_html([item('<script>"x"</script>', "https://e.com/?a=1&b=2", summary="a & b")], DAY)
    assert "<script>" not in html
    assert 'href="https://e.com/?a=1&amp;b=2"' in html
    assert "a &amp; b" in html


def test_html_does_not_link_unsafe_schemes():
    for url in ("javascript:alert(1)", "JaVaScRiPt:alert(1)", "data:text/html,hi"):
        html = render_html([item("Bad", url)], DAY)
        assert "href" not in html
        assert "Bad" in html


def test_categories_ordered_and_items_newest_first():
    old = datetime(2026, 10, 1, tzinfo=timezone.utc)
    new = datetime(2026, 10, 2, tzinfo=timezone.utc)
    items = [
        item("crypto", category="crypto"),
        item("old", published=old),
        item("undated"),
        item("new", published=new),
        item("sec", category="security"),
        item("other", category="misc"),
    ]
    text = render_text(items, DAY)
    order = [l for l in text.splitlines() if l.startswith(("## ", "- Title"))]
    assert order == [
        "## TECH (3)", "- Title: new", "- Title: old", "- Title: undated",
        "## SECURITY (1)", "- Title: sec",
        "## CRYPTO (1)", "- Title: crypto",
        "## MISC (1)", "- Title: other",
    ]


def test_summary_rendered_when_present():
    assert "Summary: hello" in render_text([item(summary="hello")], DAY)
    assert "Summary:" not in render_text([item()], DAY)
