from datetime import datetime, timezone

from azure.core.exceptions import ResourceNotFoundError # pyright: ignore[reportMissingImports]
from azure.data.tables import TableServiceClient # pyright: ignore[reportMissingImports]

from briefing.dedupe import key_for, normalize_url
from briefing.models import Item

PARTITION = "seen"


class SeenStore:
    def __init__(self, conn_str: str, table_name: str = "seenitems"):
        service = TableServiceClient.from_connection_string(conn_str)
        self.table = service.create_table_if_not_exists(table_name)

    def filter_new(self, items: list[Item]) -> list[Item]:
        unique: dict[str, Item] = {}
        for item in items:
            unique.setdefault(key_for(item.url), item)    # in-run dedupe

        new: list[Item] = []
        for key, item in unique.items():
            try:
                self.table.get_entity(PARTITION, key)     # point read
            except ResourceNotFoundError:
                new.append(item)
        return new

    def mark_sent(self, items: list[Item]) -> None:
        now = datetime.now(timezone.utc)
        ops = [
            ("upsert", {
                "PartitionKey": PARTITION,
                "RowKey": key_for(i.url),
                "Url": normalize_url(i.url),
                "Title": i.source,
                "SetAt": now,
            })
            for i in items
        ]
        for start in range(0, len(ops), 100):
            self.table.submit_transaction(ops[start:start + 100])
