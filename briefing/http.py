import requests

HEADERS = {"User-Agent": "tech-briefing/0.1 (personal digest)"}

def get(url: str) -> requests.Response:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp
