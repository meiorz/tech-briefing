from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Feed:
    id: str                     # "krebs"
    name: str
    category: str
    url: str


@dataclass(frozen=True)
class Item:
    source: str                 # Feed.id, e.g. "krebs"
    category: str               # "security", "crypto", ...
    title: str
    url: str
    published: datetime | None
    summary: str = ""
