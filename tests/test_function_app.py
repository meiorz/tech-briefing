from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

import function_app
from briefing.models import Item

run = function_app.daily_briefing._function.get_user_function()
TIMER = SimpleNamespace(past_due=False)
ITEMS = [Item("hn", "tech", "A", "https://example.com/a", datetime(2026, 10, 3, tzinfo=timezone.utc))]


class FakeStore:
    def __init__(self, new):
        self.new = new
        self.marked = None

    def filter_new(self, items):
        return self.new

    def mark_sent(self, items):
        self.marked = items


@pytest.fixture
def wired(monkeypatch):
    monkeypatch.setenv("BRIEFING_SENDER", "from@x")
    monkeypatch.setenv("BRIEFING_RECIPIENT", "to@y")
    monkeypatch.setattr(function_app.hn, "fetch_top", lambda: ITEMS)
    monkeypatch.setattr(function_app.rss, "fetch_all", lambda feeds: [])
    monkeypatch.setattr(function_app, "table_service", lambda: None)
    monkeypatch.setattr(function_app, "email_client", lambda: None)
    sent = []
    state = SimpleNamespace(sent=sent, store=None, status="Succeeded")

    def fake_send(client, sender, recipient, subject, text, html):
        sent.append((sender, recipient, subject))
        return state.status

    def make_store(service):
        return state.store

    monkeypatch.setattr(function_app, "send_briefing", fake_send)
    monkeypatch.setattr(function_app, "SeenStore", make_store)
    return state


def test_sends_and_marks_new_items(wired):
    wired.store = FakeStore(ITEMS)
    run(TIMER)
    assert len(wired.sent) == 1 and wired.sent[0][:2] == ("from@x", "to@y")
    assert "(1 new)" in wired.sent[0][2]
    assert wired.store.marked == ITEMS


def test_nothing_new_sends_nothing(wired):
    wired.store = FakeStore([])
    run(TIMER)
    assert wired.sent == []
    assert wired.store.marked is None


def test_failed_send_does_not_mark(wired):
    wired.store = FakeStore(ITEMS)
    wired.status = "Failed"
    with pytest.raises(RuntimeError):
        run(TIMER)
    assert wired.store.marked is None


@pytest.mark.parametrize("status", ["Running", "Unknown"])
def test_send_still_running_at_timeout_is_marked(wired, status, caplog):
    wired.store = FakeStore(ITEMS)
    wired.status = status
    run(TIMER)
    assert wired.store.marked == ITEMS
    assert f"still {status}" in caplog.text


def test_send_exception_does_not_mark(wired, monkeypatch):
    wired.store = FakeStore(ITEMS)

    def boom(*args):
        raise ConnectionError("ACS down")
    monkeypatch.setattr(function_app, "send_briefing", boom)
    with pytest.raises(ConnectionError):
        run(TIMER)
    assert wired.store.marked is None


def test_total_fetch_outage_fails_the_run(wired, monkeypatch):
    wired.store = FakeStore([])
    monkeypatch.setattr(function_app.hn, "fetch_top", lambda: [])
    with pytest.raises(RuntimeError, match="No items fetched"):
        run(TIMER)
