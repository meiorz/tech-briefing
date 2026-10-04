from azure.communication.email import EmailClient


def send_briefing(client: EmailClient, sender: str, recipient: str,
                  subject: str, text: str, html: str, timeout: float = 120) -> str:
    message = {
        "senderAddress": sender,
        "recipients": {"to": [{"address": recipient}]},
        "content": {"subject": subject, "plainText": text, "html": html},
    }
    result = client.begin_send(message).result(timeout=timeout)   # returns current state on timeout
    return (result or {}).get("status", "Unknown")