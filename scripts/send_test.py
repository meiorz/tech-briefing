import json
from pathlib import Path

from briefing.mailer import send_briefing

cfg = json.load(open("local.settings.json"))["Values"]
status = send_briefing(
    cfg["ACS_CONNECTION_STRING"], cfg["BRIEFING_SENDER"], cfg["BRIEFING_RECIPIENT"],
    "Tech Briefing (test)",
    Path("out/briefing.txt").read_text(encoding="utf-8"),
    Path("out/briefing.html").read_text(encoding="utf-8"),
)
print(status)
