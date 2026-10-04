from datetime import datetime, timezone
from pathlib import Path

from briefing.fetchers import hn, rss
from briefing.render import render_html, render_text
from briefing.sources import RSS_FEEDS

items = hn.fetch_top() + rss.fetch_all(RSS_FEEDS)
today = datetime.now(timezone.utc).date()

out = Path("out")
out.mkdir(exist_ok=True)
(out / "briefing.txt").write_text(render_text(items, today), encoding="utf-8")
(out / "briefing.html").write_text(render_html(items, today), encoding="utf-8")

for f in out.iterdir():
    print(f"{f.name:15} {f.stat().st_size / 1024:.1f} KB")