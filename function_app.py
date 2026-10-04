import logging
import os
from collections import Counter
from datetime import datetime, timezone

import azure.functions as func

from briefing.clients import email_client, table_service
from briefing.fetchers import hn, rss
from briefing.mailer import send_briefing
from briefing.render import render_html, render_text
from briefing.sources import RSS_FEEDS
from briefing.store import SeenStore

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)

FAILED_STATUSES = {"Failed", "Canceled"}

app = func.FunctionApp()


@app.timer_trigger(schedule="0 0 14 * * *", arg_name="timer",
                   run_on_startup=False, use_monitor=True)
def daily_briefing(timer: func.TimerRequest) -> None:
    if timer.past_due:
        logging.warning("Timer is past due; this run is late")

    items = hn.fetch_top() + rss.fetch_all(RSS_FEEDS)
    if not items:                    # every source failed; don't pass this off as a quiet day
        raise RuntimeError("No items fetched from any source")

    by_category = Counter(i.category for i in items)
    logging.info("Fetched %d items: %s", len(items), dict(by_category))

    store = SeenStore(table_service())
    new_items = store.filter_new(items)
    logging.info("New since last briefing: %d of %d", len(new_items), len(items))

    if not new_items:
        logging.info("Nothing new; no email sent")
        return

    today = datetime.now(timezone.utc).date()
    status = send_briefing(
        email_client(),
        os.environ["BRIEFING_SENDER"],
        os.environ["BRIEFING_RECIPIENT"],
        f"Tech Briefing {today:%Y-%m-%d} ({len(new_items)} new)",
        render_text(new_items, today),
        render_html(new_items, today),
    )
    if status in FAILED_STATUSES:
        raise RuntimeError(f"Email send failed with status: {status}")
    if status != "Succeeded":        # accepted but still running at timeout: likely delivered,
        logging.warning("Email send still %s after timeout; marking as sent", status)  # so prefer a miss over a duplicate

    store.mark_sent(new_items)       # only after ACS accepted the send
    logging.info("Sent and recorded %d items", len(new_items))
    