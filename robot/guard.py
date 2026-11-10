"""The comment guard. Runs every hour on GitHub.

Looks at comments on our latest Instagram and Facebook posts and HIDES (never deletes, never replies to) any that:
- contain a word or phrase from robot/hidden_words.txt (spam, scams, moves to private apps, unsafe questions, bad words), or
- contain a web link.
Our own comments are never hidden. Hidden comments stay visible to the person who wrote them and can be unhidden in the app.
What it keeps: only the comment's ID, the platform, the reason and the time (log/hidden.json), never the text or the name,
as promised in the privacy policy.
"""
import re
import sys
import traceback

from common import ROOT, ApiError, load_log, paused, save_log, setting, stamp
import meta

LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(com|net|org|co|uk|io|ly|me|info|xyz|link|site|shop|app)\b|wa\.me|t\.me|bit\.ly", re.I)


def words():
    out = []
    for line in (ROOT / "robot" / "hidden_words.txt").read_text().splitlines():
        w = line.strip().lower()
        if w and not w.startswith("#"):
            out.append(w)
    return out


def reason(text, wordlist):
    t = " " + re.sub(r"\s+", " ", text.lower()) + " "
    if LINK.search(text):
        return "link"
    for w in wordlist:
        if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", t):
            return f"word: {w}"
    return None


def main():
    if paused():
        print("Paused (ROBOT_PAUSED is on). No comments checked.")
        return 0
    wl, log, problems, hidden = words(), load_log("hidden.json"), [], 0
    ours_ig = setting("IG_USERNAME", "sparrowstreetstories").lower()
    ours_fb = setting("PAGE_ID")
    checks = [
        ("instagram", meta.instagram_comments, meta.hide_instagram, lambda who: who.lower() == ours_ig),
        ("facebook", meta.facebook_comments, meta.hide_facebook, lambda who: who == ours_fb),
    ]
    for platform, fetch, hide, is_us in checks:
        try:
            for cid, text, who in fetch():
                if cid in log or is_us(who):
                    continue
                why = reason(text, wl)
                if why:
                    hide(cid)
                    log[cid] = {"platform": platform, "reason": why, "at": stamp()}
                    hidden += 1
                    print(f"HIDDEN  {platform} comment ({why})")
        except ApiError as e:
            problems.append(f"{platform}: {e}")
            print(f"ERROR   {platform}: {e}")
    save_log("hidden.json", log)
    print(f"Done: {hidden} comment(s) hidden this run.")
    return 1 if problems else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        from common import clean
        print(clean(traceback.format_exc()))
        sys.exit(1)
