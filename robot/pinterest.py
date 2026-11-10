"""Pinterest pins through the Pinterest API (v5), using the app "Sparrow Street Pins".

The long-lasting refresh key (PINTEREST_REFRESH_TOKEN, valid for a year) is swapped for a short-lived key on each run.
Pins made while the app has Trial access are only visible to Sparrow Street itself; they become public once
Pinterest grants Standard access. Until then the robot leaves Pinterest switched off (PINTEREST_ON is not "yes").
"""
from common import PIN_API, ApiError, basic, bearer, http, media_url, setting

_access = None
_boards = None


def _key():
    global _access
    if not _access:
        app_id, secret, refresh = setting("PINTEREST_APP_ID"), setting("PINTEREST_APP_SECRET"), setting("PINTEREST_REFRESH_TOKEN")
        if not (app_id and secret and refresh):
            raise ApiError("Pinterest isn't connected yet (run tools/connect_pinterest.py)")
        r = http("POST", f"{PIN_API}/oauth/token", form={"grant_type": "refresh_token", "refresh_token": refresh}, headers=basic(app_id, secret))
        _access = r.get("access_token") or ""
        if not _access:
            raise ApiError("Pinterest didn't give a key (the connection may have expired: run tools/connect_pinterest.py)")
    return _access


def boards() -> dict:
    """Our boards: {name: id}."""
    global _boards
    if _boards is None:
        _boards, bookmark = {}, None
        while True:
            r = http("GET", f"{PIN_API}/boards", params={"page_size": 100, **({"bookmark": bookmark} if bookmark else {})}, headers=bearer(_key()))
            for b in r.get("items", []):
                _boards[b["name"]] = b["id"]
            bookmark = r.get("bookmark")
            if not bookmark:
                break
    return _boards


def pin(post, dry_run=False):
    p = post.get("pinterest") or {}
    board = p.get("board", "")
    ids = boards()
    if board not in ids:
        raise ApiError(f"no Pinterest board called {board!r} (boards: {', '.join(ids) or 'none'})")
    if dry_run:
        return "dry-run", f"Pinterest connected; board {board!r} found"
    body = {
        "board_id": ids[board],
        "title": p.get("title", "")[:100],
        "description": p.get("description", "")[:500],
        "link": p.get("link", ""),
        "alt_text": p.get("alt_text", p.get("title", ""))[:500],
        "media_source": {"source_type": "image_url", "url": media_url(post["media"][0])},
    }
    r = http("POST", f"{PIN_API}/pins", json_body=body, headers=bearer(_key()))
    return r["id"], f"https://www.pinterest.com/pin/{r['id']}/"
