from datetime import date, datetime, timezone

from briefing.models import Item
from briefing.render import render_html, render_text

items = [
    Item("hn", "tech", "Show HN: <script> & \"quotes\"", "https://example.com/a?x=1&y=2",
         datetime(2026, 10, 3, 9, 0, tzinfo=timezone.utc)),
    Item("krebs", "security", "Breach at Example Corp", "https://example.com/b",
         None, "Attackers used stolen credentials & MFA fatigue."),
    Item("coindesk", "crypto", "Bitcoin moves", "https://example.com/c",
         datetime(2026, 10, 2, 14, 30, tzinfo=timezone.utc), "Short summary."),
]

print(render_text(items, date(2026, 10, 3)))
print("-" * 60)
print(render_html(items, date(2026, 10, 3)))