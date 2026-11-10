"""Instagram and Facebook Page posting through Meta's Graph API, using the robot's never-expiring key (META_TOKEN).

Post types: image (one picture), carousel (2–10 pictures), reel (a vertical video), story (a picture or a video).
Every function takes dry_run: then everything is checked and prepared on Meta's side, but nothing is published
(Instagram containers are made but never published; Facebook items are uploaded unpublished and removed again).
"""
from common import GRAPH, ApiError, bearer, http, media_url, setting, wait

_page_token = None


def _tok():
    t = setting("META_TOKEN")
    if not t:
        raise ApiError("META_TOKEN is missing from the secret store")
    return t


def page_token():
    """The Page's own key, fetched with the robot's key (never stored)."""
    global _page_token
    if not _page_token:
        r = http("GET", f"{GRAPH}/{setting('PAGE_ID')}", params={"fields": "access_token"}, headers=bearer(_tok()))
        _page_token = r.get("access_token") or ""
        if not _page_token:
            raise ApiError("could not get the Page's key (check the robot still has full control of the Page)")
    return _page_token


# ---------------------------------------------------------------- Instagram
def _ig(path, **form):
    return http("POST", f"{GRAPH}/{setting('IG_USER_ID')}/{path}", form=form, headers=bearer(_tok()))


def _ig_wait(cid, minutes=8):
    """Wait until Instagram has fetched and processed the picture or video."""
    for _ in range(minutes * 6):
        r = http("GET", f"{GRAPH}/{cid}", params={"fields": "status_code,status"}, headers=bearer(_tok()))
        code = r.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise ApiError(f"Instagram couldn't process the media: {r.get('status', code)}")
        wait(10)
    raise ApiError("Instagram took too long to process the media")


def _ig_publish(cid):
    r = _ig("media_publish", creation_id=cid)
    mid = r["id"]
    link = http("GET", f"{GRAPH}/{mid}", params={"fields": "permalink"}, headers=bearer(_tok())).get("permalink", "")
    return mid, link


def instagram(post, dry_run=False):
    kind, files, caption = post["type"], post["media"], post.get("caption_instagram", post.get("caption", ""))
    urls = [media_url(f) for f in files]
    is_video = lambda u: u.lower().endswith((".mp4", ".mov"))
    if kind == "image":
        cid = _ig("media", image_url=urls[0], caption=caption)["id"]
    elif kind == "carousel":
        kids = []
        for u in urls:
            p = {"is_carousel_item": "true", **({"media_type": "VIDEO", "video_url": u} if is_video(u) else {"image_url": u})}
            k = _ig("media", **p)["id"]
            _ig_wait(k)
            kids.append(k)
        cid = _ig("media", media_type="CAROUSEL", children=",".join(kids), caption=caption)["id"]
    elif kind == "reel":
        cid = _ig("media", media_type="REELS", video_url=urls[0], caption=caption, share_to_feed="true")["id"]
    elif kind == "story":
        cid = _ig("media", media_type="STORIES", **({"video_url": urls[0]} if is_video(urls[0]) else {"image_url": urls[0]}))["id"]
    else:
        raise ApiError(f"unknown post type {kind!r}")
    _ig_wait(cid)
    if dry_run:
        return "dry-run", "prepared on Instagram, not published"
    return _ig_publish(cid)


# ---------------------------------------------------------------- Facebook Page
def _fb(path, **form):
    return http("POST", f"{GRAPH}/{path}", form=form, headers=bearer(page_token()))


def _fb_delete(obj_id):
    try:
        http("DELETE", f"{GRAPH}/{obj_id}", headers=bearer(page_token()))
    except ApiError:
        pass


def facebook(post, dry_run=False):
    kind, files = post["type"], post["media"]
    caption = post.get("caption_facebook", post.get("caption", ""))
    urls = [media_url(f) for f in files]
    page = setting("PAGE_ID")
    pub = "false" if dry_run else "true"
    if kind == "image":
        r = _fb(f"{page}/photos", url=urls[0], message=caption, published=pub)
        oid = r.get("post_id") or r["id"]
    elif kind == "carousel":
        ids = [_fb(f"{page}/photos", url=u, published="false")["id"] for u in urls]
        if dry_run:
            for i in ids:
                _fb_delete(i)
            return "dry-run", f"{len(ids)} pictures uploaded unpublished to Facebook, then removed"
        form = {"message": caption}
        for i, pid in enumerate(ids):
            form[f"attached_media[{i}]"] = '{"media_fbid":"%s"}' % pid
        oid = _fb(f"{page}/feed", **form)["id"]
    elif kind == "reel":
        r = _fb(f"{page}/videos", file_url=urls[0], description=caption, published=pub)
        oid = r["id"]
    elif kind == "story":
        if urls[0].lower().endswith((".mp4", ".mov")):
            return "skipped", "video stories go to Instagram only"
        photo = _fb(f"{page}/photos", url=urls[0], published="false")["id"]
        if dry_run:
            _fb_delete(photo)
            return "dry-run", "story picture uploaded unpublished to Facebook, then removed"
        oid = _fb(f"{page}/photo_stories", photo_id=photo).get("post_id", photo)
    else:
        raise ApiError(f"unknown post type {kind!r}")
    if dry_run:
        _fb_delete(oid)
        return "dry-run", "uploaded unpublished to Facebook, then removed"
    return oid, f"https://www.facebook.com/{oid}"


# ---------------------------------------------------------------- comments (for the guard)
def instagram_comments(limit_posts=25):
    """Comments (and replies) on our latest Instagram posts: (comment_id, text, username)."""
    out = []
    media = http("GET", f"{GRAPH}/{setting('IG_USER_ID')}/media", params={"fields": "id", "limit": limit_posts}, headers=bearer(_tok())).get("data", [])
    for m in media:
        r = http("GET", f"{GRAPH}/{m['id']}/comments", params={"fields": "id,text,username,hidden,replies{id,text,username,hidden}", "limit": 50}, headers=bearer(_tok()))
        for c in r.get("data", []):
            for x in [c] + c.get("replies", {}).get("data", []):
                if not x.get("hidden"):
                    out.append((x["id"], x.get("text", ""), x.get("username", "")))
    return out


def hide_instagram(comment_id):
    http("POST", f"{GRAPH}/{comment_id}", form={"hide": "true"}, headers=bearer(_tok()))


def facebook_comments(limit_posts=25):
    """Comments on our latest Facebook Page posts: (comment_id, text, author_id)."""
    out = []
    page = setting("PAGE_ID")
    feed = http("GET", f"{GRAPH}/{page}/feed", params={"fields": "id", "limit": limit_posts}, headers=bearer(page_token())).get("data", [])
    for p in feed:
        r = http("GET", f"{GRAPH}/{p['id']}/comments", params={"fields": "id,message,is_hidden,from", "filter": "stream", "limit": 100}, headers=bearer(page_token()))
        for c in r.get("data", []):
            if not c.get("is_hidden"):
                out.append((c["id"], c.get("message", ""), (c.get("from") or {}).get("id", "")))
    return out


def hide_facebook(comment_id):
    http("POST", f"{GRAPH}/{comment_id}", form={"is_hidden": "true"}, headers=bearer(page_token()))
