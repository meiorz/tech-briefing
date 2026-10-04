from azure.communication.email import EmailClient


def send_briefing(conn_str: str, sender: str, recipient: str,
                  subject: str, text: str, html: str) -> str:
    client = EmailClient.from_connection_string(conn_str)
    message = {
        "senderAddress": sender,
        "recipients": {"to": [{"address": recipient}]},
        "content": {"subject": subject, "plainText": text, "html": html},
    }
    result = client.begin_send(message).result()   # waits until accepted
    return result["status"]