"""The Monday report. Opens a GitHub "issue" titled "Weekly report", which GitHub emails to hello.sparrowstreet@gmail.com,
and closes last week's. It says what went out in the last 7 days, anything missed or failed, how many comments were hidden,
what's coming in the next 7 days, and whether the queue is running low.
"""
import json
import os
import sys
import urllib.request
from collections import Counter

from common import UK, load_log, load_queue, now_utc, parse_uk, timedelta

REPO = os.environ.get("GITHUB_REPOSITORY", "sparrowstreetstories/sparrow-street-social")
API = f"https://api.github.com/repos/{REPO}"


def gh(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"{}")


def main():
    now = now_utc()
    week_ago, week_ahead = now - timedelta(days=7), now + timedelta(days=7)
    queue = {p["id"]: p for p in load_queue()}
    posted = load_log("posted.json")
    lines_done, problems, counts = [], [], Counter()
    for pid, plats in sorted(posted.items()):
        p = queue.get(pid)
        if not p or not (week_ago <= parse_uk(p["when"]) <= now):
            continue
        for plat, rec in plats.items():
            st = rec.get("status")
            if st == "posted":
                counts[plat] += 1
                lines_done.append(f"- {p['when']} · {plat} · {p.get('title', pid)} · [view]({rec.get('link', '')})")
            elif st in ("missed", "failed", "retry"):
                problems.append(f"- **{st}** · {p['when']} · {plat} · {p.get('title', pid)}: {rec.get('error') or rec.get('note', '')}")
    hidden = load_log("hidden.json")
    recent_hidden = Counter(v["platform"] for v in hidden.values() if v["at"] >= (week_ago.astimezone(UK).strftime("%Y-%m-%d %H:%M")))
    upcoming = sorted((p for p in queue.values() if now < parse_uk(p["when"]) <= week_ahead), key=lambda p: p["when"])
    last = max((parse_uk(p["when"]) for p in queue.values()), default=now)
    days_left = (last - now).days
    body = [f"**Sparrow Street · weekly report · {now.astimezone(UK).strftime('%A %-d %B %Y')}**", ""]
    body.append(f"**Posted in the last 7 days:** Instagram {counts['instagram']}, Facebook {counts['facebook']}, Pinterest {counts['pinterest']}")
    body += lines_done or ["- (nothing this week)"]
    body += ["", "**Needs a look:**"] + (problems or ["- Nothing. Everything went out as planned. ✅"])
    body += ["", f"**Comments hidden this week:** Instagram {recent_hidden['instagram']}, Facebook {recent_hidden['facebook']} (spam, links or unsafe words; hidden, not deleted)"]
    body += ["", f"**Coming up in the next 7 days:** {len(upcoming)} post(s)"] + [f"- {p['when']} · {', '.join(p['platforms'])} · {p.get('title', p['id'])}" for p in upcoming]
    body += ["", f"**Queue:** planned until {last.astimezone(UK).strftime('%a %-d %b')}" + (" ⚠️ running low: ask Claude for the next batch of posts." if days_left < 10 else " ✅")]
    body += ["", "_Nothing to do unless something above says it needs a look. To pause the robot, tell Claude, or set the ROBOT_PAUSED variable to yes in the repository settings._"]
    for issue in gh("GET", "/issues?state=open&labels=weekly-report"):
        gh("PATCH", f"/issues/{issue['number']}", {"state": "closed"})
    gh("POST", "/issues", {"title": f"Weekly report · {now.astimezone(UK).strftime('%-d %b %Y')}", "body": "\n".join(body), "labels": ["weekly-report"]})
    print("\n".join(body))
    return 0


if __name__ == "__main__":
    sys.exit(main())
