import logging
import os

import azure.functions as func
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

from briefing.fetchers import hn, rss
from briefing.sources import RSS_FEEDS
from briefing.store import SeenStore

app = func.FunctionApp()


@app.timer_trigger(schedule="0 0 14 * * *", arg_name="timer",
                   run_on_startup=False, use_monitor=True)
def daily_briefing(timer: func.TimerRequest) -> None:
    if timer.past_due:
        logging.warning("Timer is past due; this run is late")

    items = hn.fetch_top() + rss.fetch_all(RSS_FEEDS)

    by_category: dict[str, int] = {}
    for item in items:
        by_category[item.category] = by_category.get(item.category, 0) + 1
    logging.info("Fetched %d items: %s", len(items), by_category)
    store = SeenStore(os.environ["BRIEFING_TABLES_CONNECTION"])
    new_items = store.filter_new(items)
    logging.info("New since last briefing: %d of %d", len(new_items), len(items))

    # TEMPORARY: Phase 4 moves this to after the email is sent successfully.
    store.mark_sent(new_items)

