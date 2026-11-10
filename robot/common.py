"""Shared helpers for the Sparrow Street robot: web requests, settings, the queue and the log.

Only the Python standard library is used, so nothing has to be installed on GitHub's computers.
Keys come from environment variables (GitHub's secret store) and are never printed: they travel in
request headers or bodies, never in web addresses, and error messages are cleaned before they are shown.
"""
import base64
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "queue"
LOG = ROOT / "log"
MEDIA = ROOT / "docs" / "media"
SITE = "https://sparrowstreetstories.com"
UK = ZoneInfo("Europe/London")
GRAPH = "https://graph.facebook.com/v23.0"
PIN_API = "https://api.pinterest.com/v5"

SECRETS = [v for v in (os.environ.get(k, "") for k in ("META_TOKEN", "PINTEREST_APP_SECRET", "PINTEREST_REFRESH_TOKEN")) if v]


def clean(text: str) -> str:
    """Remove anything that looks like a key from a message before it is printed or saved."""
    for s in SECRETS:
        text = text.replace(s, "[hidden]")
    return re.sub(r"(access_token|refresh_token|client_secret)=[^&\s\"']+", r"\1=[hidden]", text)


class ApiError(Exception):
    pass


def http(method: str, url: str, *, params=None, form=None, json_body=None, headers=None, timeout=120):
    """One web request; returns parsed JSON (or {} for an empty reply). Raises ApiError with a clean message."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    data = None
    h = dict(headers or {})
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        h.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif json_body is not None:
        data = json.dumps(json_body).encode()
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode() or "{}"
            return json.loads(body) if body.strip().startswith(("{", "[")) else {"raw": body}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise ApiError(clean(f"HTTP {e.code} from {urllib.parse.urlsplit(url).netloc}: {detail}")) from None
    except urllib.error.URLError as e:
        raise ApiError(clean(f"could not reach {urllib.parse.urlsplit(url).netloc}: {e.reason}")) from None


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def basic(user: str, password: str) -> dict:
    return {"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()}


def media_url(name: str) -> str:
    return f"{SITE}/media/{urllib.parse.quote(name)}"


def url_ready(url: str) -> bool:
    """True once GitHub Pages is serving the file (it takes a minute or two after a push)."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_uk(when: str) -> datetime:
    """'2026-11-16 14:15' (UK clock time, summer or winter) → an exact moment in UTC."""
    return datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=UK).astimezone(timezone.utc)


def load_queue(include_tests=False) -> list:
    posts = []
    for f in sorted(QUEUE.glob("*.json")):
        for p in json.loads(f.read_text()):
            if p.get("test") and not include_tests:
                continue
            p["_file"] = f.name
            posts.append(p)
    ids = [p["id"] for p in posts]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"Queue problem: these post ids are used twice: {sorted(dupes)}")
    return posts


def load_log(name: str) -> dict:
    f = LOG / name
    return json.loads(f.read_text()) if f.exists() else {}


def save_log(name: str, data: dict):
    LOG.mkdir(exist_ok=True)
    (LOG / name).write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n")


def setting(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def paused() -> bool:
    return setting("ROBOT_PAUSED").lower() in ("yes", "true", "1", "on")


def stamp() -> str:
    return now_utc().astimezone(UK).strftime("%Y-%m-%d %H:%M")


def wait(seconds: float):
    time.sleep(seconds)


