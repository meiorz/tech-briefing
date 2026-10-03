import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref"}

def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    scheme = "https" if parts.scheme in ("http", "https") else parts.scheme
    query = sorted(
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS
    )
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((scheme, parts.netloc.lower(), path, urlencode(query), ""))

def key_for(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()
