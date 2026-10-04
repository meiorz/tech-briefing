from datetime import datetime, timezone

from azure.core.exceptions import ResourceNotFoundError

from briefing.dedupe import key_for
from briefing.models import Item
from briefing.store import PARTITION, SeenStore


class FakeTable:
    def __init__(self, seen=()):
        self.seen = set(seen)
        self.batches = []

    def get_entity(self, partition, row):
        if (partition, row) not in self.seen:
            raise ResourceNotFoundError("missing")
        return {}

    def submit_transaction(self, ops):
        self.batches.append(ops)


class FakeService:
    def __init__(self, table):
        self.table = table

    def create_table_if_not_exists(self, name):
        return self.table


def item(url, title="t"):
    return Item("src", "tech", title, url, datetime(2026, 10, 3, tzinfo=timezone.utc))


def test_filter_new_drops_seen_and_in_run_duplicates():
    table = FakeTable(seen={(PARTITION, key_for("https://example.com/old"))})
    store = SeenStore(FakeService(table))
    new = store.filter_new([
        item("https://example.com/old"),
        item("https://example.com/new"),
        item("http://example.com/new/?utm_source=rss"),
    ])
    assert [i.url for i in new] == ["https://example.com/new"]


def test_mark_sent_records_title_and_batches_by_100():
    table = FakeTable()
    store = SeenStore(FakeService(table))
    store.mark_sent([item(f"https://example.com/{n}", title=f"T{n}") for n in range(250)])
    assert [len(b) for b in table.batches] == [100, 100, 50]
    op, entity = table.batches[0][0]
    assert op == "upsert"
    assert entity["Title"] == "T0"
    assert entity["RowKey"] == key_for("https://example.com/0")
    assert "SentAt" in entity
