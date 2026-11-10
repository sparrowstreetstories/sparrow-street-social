"""The posting robot. Runs every 15 minutes on GitHub (and by hand for tests).

    python robot/post.py            # publish anything due now
    python robot/post.py --dry-run  # check and prepare everything due (and test posts), publish nothing

For each post in queue/*.json whose time has come (UK time), it posts to each platform listed, once.
Rules it keeps:
- Only posts what's in the queue (material Peter has already approved). It never writes anything itself.
- More than 6 hours late (for example after a pause) → marked "missed", not posted late.
- A platform that fails is retried on the next two runs at most, then marked "failed" and left alone.
  Any failure makes the run fail, so GitHub emails hello.sparrowstreet@gmail.com.
- If a platform fails, the rest of that platform's posts wait until the next run.
Every result goes into log/posted.json.
"""
import sys
import traceback

from common import ApiError, load_log, load_queue, media_url, now_utc, parse_uk, paused, save_log, setting, stamp, timedelta, url_ready
import meta
import pinterest

PLATFORMS = {"instagram": meta.instagram, "facebook": meta.facebook, "pinterest": pinterest.pin}
LATE = timedelta(hours=6)
MAX_TRIES = 3


def enabled(platform):
    if platform == "pinterest":
        return setting("PINTEREST_ON").lower() == "yes"
    return True


def main():
    dry = "--dry-run" in sys.argv
    if paused() and not dry:
        print("Paused (ROBOT_PAUSED is on). Nothing posted.")
        return 0
    log = load_log("posted.json")
    now = now_utc()
    failed_now, blocked = [], set()
    for post in load_queue(include_tests=dry):
        due = parse_uk(post["when"])
        if due > now and not (dry and post.get("test")):
            continue
        entry = log.setdefault(post["id"], {}) if not dry else {}
        for platform in post["platforms"]:
            rec = entry.get(platform, {})
            if rec.get("status") in ("posted", "missed", "failed", "skipped"):
                continue
            if not enabled(platform):
                if not dry:
                    entry[platform] = {"status": "skipped", "at": stamp(), "note": f"{platform} is switched off"}
                continue
            if platform in blocked:
                continue
            if not dry and now - due > LATE:
                entry[platform] = {"status": "missed", "at": stamp(), "note": "more than 6 hours late (paused or failing), not posted late"}
                print(f"MISSED  {post['id']} · {platform}")
                continue
            missing = [m for m in post["media"] if not url_ready(media_url(m))]
            if missing:
                print(f"WAIT    {post['id']} · {platform}: media not online yet ({', '.join(missing)})")
                continue
            try:
                ref, link = PLATFORMS[platform](post, dry_run=dry)
                if ref == "skipped":
                    entry[platform] = {"status": "skipped", "at": stamp(), "note": link}
                    print(f"SKIPPED {post['id']} · {platform}: {link}")
                elif dry:
                    print(f"OK (dry run) {post['id']} · {platform}: {link}")
                else:
                    entry[platform] = {"status": "posted", "at": stamp(), "id": ref, "link": link}
                    print(f"POSTED  {post['id']} · {platform}: {link}")
            except (ApiError, KeyError, ValueError) as e:
                msg = str(e) if isinstance(e, ApiError) else f"{type(e).__name__}: {e}"
                tries = rec.get("tries", 0) + 1
                status = "failed" if tries >= MAX_TRIES else "retry"
                if not dry:
                    entry[platform] = {"status": status, "tries": tries, "at": stamp(), "error": msg}
                failed_now.append(f"{post['id']} · {platform}: {msg}")
                blocked.add(platform)
                print(f"ERROR   {post['id']} · {platform} (try {tries}): {msg}")
        if not dry and not entry:
            log.pop(post["id"], None)
    if not dry:
        save_log("posted.json", log)
    if failed_now:
        print("\nSome posts didn't go out:\n  " + "\n  ".join(failed_now))
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        from common import clean
        print(clean(traceback.format_exc()))
        sys.exit(1)
