import json
import os
from pathlib import Path

from briefing.clients import email_client
from briefing.mailer import send_briefing

settings = json.loads(Path("local.settings.json").read_text(encoding="utf-8"))["Values"]
os.environ.update({k: str(v) for k, v in settings.items()})
status = send_briefing(
    email_client(), os.environ["BRIEFING_SENDER"], os.environ["BRIEFING_RECIPIENT"],
    "Tech Briefing (test)",
    Path("out/briefing.txt").read_text(encoding="utf-8"),
    Path("out/briefing.html").read_text(encoding="utf-8"),
)
print(status)