import pytest

from briefing import clients

TABLES_CONN = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=fake"
ACS_CONN = "endpoint=https://acs.example.communication.azure.com/;accesskey=fake"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("BRIEFING_TABLES_CONNECTION", "BRIEFING_TABLES_ENDPOINT",
                 "ACS_CONNECTION_STRING", "ACS_ENDPOINT"):
        monkeypatch.delenv(name, raising=False)
    sentinel = object()
    monkeypatch.setattr(clients, "_credential", lambda: sentinel)
    return sentinel


def test_tables_prefer_connection_string(monkeypatch):
    seen = {}
    monkeypatch.setattr(clients.TableServiceClient, "from_connection_string",
                        classmethod(lambda cls, conn: seen.setdefault("conn", conn)))
    monkeypatch.setenv("BRIEFING_TABLES_CONNECTION", TABLES_CONN)
    monkeypatch.setenv("BRIEFING_TABLES_ENDPOINT", "https://ignored.table.core.windows.net")
    clients.table_service()
    assert seen["conn"] == TABLES_CONN


def test_tables_fall_back_to_managed_identity(monkeypatch, clean_env):
    calls = {}
    monkeypatch.setattr(clients, "TableServiceClient",
                        lambda endpoint, credential: calls.update(endpoint=endpoint, credential=credential))
    monkeypatch.setenv("BRIEFING_TABLES_ENDPOINT", "https://st.table.core.windows.net")
    clients.table_service()
    assert calls == {"endpoint": "https://st.table.core.windows.net", "credential": clean_env}


def test_email_prefers_connection_string(monkeypatch):
    seen = {}
    monkeypatch.setattr(clients.EmailClient, "from_connection_string",
                        classmethod(lambda cls, conn: seen.setdefault("conn", conn)))
    monkeypatch.setenv("ACS_CONNECTION_STRING", ACS_CONN)
    clients.email_client()
    assert seen["conn"] == ACS_CONN


def test_email_falls_back_to_managed_identity(monkeypatch, clean_env):
    calls = {}
    monkeypatch.setattr(clients, "EmailClient",
                        lambda endpoint, credential: calls.update(endpoint=endpoint, credential=credential))
    monkeypatch.setenv("ACS_ENDPOINT", "https://acs.example.communication.azure.com")
    clients.email_client()
    assert calls == {"endpoint": "https://acs.example.communication.azure.com", "credential": clean_env}


def test_missing_config_fails_loudly():
    with pytest.raises(KeyError):
        clients.table_service()
    with pytest.raises(KeyError):
        clients.email_client()
