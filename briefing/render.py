from collections import defaultdict
from datetime import date, datetime, timezone
from html import escape
from urllib.parse import urlsplit

from briefing.models import Item

ORDER = ["tech", "security", "crypto"]
OLDEST = datetime.min.replace(tzinfo=timezone.utc)
SAFE_SCHEMES = {"http", "https"}


def _grouped(items: list[Item]) -> list[tuple[str, list[Item]]]:
    groups: dict[str, list[Item]] = defaultdict(list)
    for item in items:
        groups[item.category].append(item)
    for group in groups.values():
        group.sort(key=lambda i: i.published or OLDEST, reverse=True)
    rank = lambda cat: ORDER.index(cat) if cat in ORDER else len(ORDER)
    return sorted(groups.items(), key=lambda kv: rank(kv[0]))


def _when(item: Item) -> str:
    return f"{item.published:%Y-%m-%d %H:%M} UTC" if item.published else "unknown"


def _link(item: Item) -> str:
    title = escape(item.title)
    if urlsplit(item.url).scheme.lower() not in SAFE_SCHEMES:   # no javascript:, data:, ...
        return title
    return f'<a href="{escape(item.url, quote=True)}">{title}</a>'


def render_text(items: list[Item], day: date) -> str:
    lines = [f"Tech Briefing {day:%Y-%m-%d}: {len(items)} new items", ""]
    for category, group in _grouped(items):
        lines.append(f"## {category.upper()} ({len(group)})")
        for i in group:
            lines.append(f"- Title: {i.title}")
            lines.append(f"  Source: {i.source} | Published: {_when(i)}")
            lines.append(f"  URL: {i.url}")
            if i.summary:
                lines.append(f"  Summary: {i.summary}")
        lines.append("")
    return "\n".join(lines)


def render_html(items: list[Item], day: date) -> str:
    parts = [f"<h1>Tech Briefing {day:%Y-%m-%d}</h1><p>{len(items)} new items</p>"]
    for category, group in _grouped(items):
        parts.append(f"<h2>{escape(category.upper())} ({len(group)})</h2><ul>")
        for i in group:
            summary = f"<br>{escape(i.summary)}" if i.summary else ""
            parts.append(
                f"<li>{_link(i)}"
                f"<br><small>{escape(i.source)} · {_when(i)}</small>{summary}</li>"
            )
        parts.append("</ul>")
    return "\n".join(parts)
