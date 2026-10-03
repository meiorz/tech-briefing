import logging

import azure.functions as func  # pyright: ignore[reportMissingImports]

from briefing.fetchers import hn, rss
from briefing.sources import RSS_FEEDS

app = func.FunctionApp()


@app.timer_trigger(schedule="0 0 14 * * *", arg_name="timer",
                   rung_on_startup=False, use_monitor=False)
def daily_briefing(timer: func. TimerRequest) -> None:
    if timer.past_due:
        logging.warning("Timer is past due; this run is late")

    items = hn.fetch_top() + rss.fetch_all(RSS_FEEDS)

    by_category: dict[str, int] = {}
    for item in items:
        by_category[item.category] = by_category.get(item.category, 0) + 1
    logging.info("Fetched %d items: %s", len(items), by_category)