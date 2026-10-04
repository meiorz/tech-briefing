from briefing.mailer import send_briefing


class FakePoller:
    def __init__(self):
        self.timeout = None

    def result(self, timeout=None):
        self.timeout = timeout
        return {"status": "Succeeded"}


class FakeClient:
    def __init__(self):
        self.poller = FakePoller()
        self.message = None

    def begin_send(self, message):
        self.message = message
        return self.poller


def test_send_builds_message_and_bounds_wait():
    client = FakeClient()
    status = send_briefing(client, "from@x", "to@y", "Subj", "plain", "<p>html</p>")
    assert status == "Succeeded"
    assert client.poller.timeout == 120
    assert client.message["recipients"]["to"] == [{"address": "to@y"}]
    assert client.message["content"] == {"subject": "Subj", "plainText": "plain", "html": "<p>html</p>"}


class StillRunningPoller(FakePoller):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    def result(self, timeout=None):
        self.timeout = timeout
        return self.resource


def test_timeout_returns_current_status():
    client = FakeClient()
    client.poller = StillRunningPoller({"status": "Running"})
    assert send_briefing(client, "f", "t", "s", "x", "y", timeout=1) == "Running"


def test_no_resource_reports_unknown():
    client = FakeClient()
    client.poller = StillRunningPoller(None)
    assert send_briefing(client, "f", "t", "s", "x", "y") == "Unknown"
