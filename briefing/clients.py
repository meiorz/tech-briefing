import os
from functools import lru_cache

from azure.communication.email import EmailClient
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential


@lru_cache(maxsize=1)
def _credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def table_service() -> TableServiceClient:
    conn = os.environ.get("BRIEFING_TABLES_CONNECTION")
    if conn:                                   # local: Azurite
        return TableServiceClient.from_connection_string(conn)
    return TableServiceClient(endpoint=os.environ["BRIEFING_TABLES_ENDPOINT"],
                              credential=_credential())


def email_client() -> EmailClient:
    conn = os.environ.get("ACS_CONNECTION_STRING")
    if conn:                                   # local: access key
        return EmailClient.from_connection_string(conn)
    return EmailClient(os.environ["ACS_ENDPOINT"], _credential())