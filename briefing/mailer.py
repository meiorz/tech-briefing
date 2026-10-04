from azure.communication.email import EmailClient


def send_briefing(client: EmailClient, sender: str, recipient: str,
                  subject: str, text: str, html: str) -> str:
    message = {
        "senderAddress": sender,
        "recipients": {"to": [{"address": recipient}]},
        "content": {"subject": subject, "plainText": text, "html": html},
    }
    return client.begin_send(message).result()["status"]