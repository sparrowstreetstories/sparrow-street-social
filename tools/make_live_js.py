"""Rebuild docs/live.js from every episode's youtube.json.

live.js maps each episode's go-live date (YYYY-MM-DD) to its YouTube video
and go-live time. The website uses it to turn an episode card or row into a
"watch on YouTube" link once that time has passed, so a viewer never lands on
a private, still-scheduled video.

Run after new episodes are uploaded:
    python3 social-robot/tools/make_live_js.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "social-robot", "docs", "live.js")

videos = {}
for path in sorted(glob.glob(os.path.join(ROOT, "Ready to upload", "Episode*", "youtube.json"))):
    main = json.load(open(path)).get("Video.mp4")
    if not main:
        continue
    live = main["goes_live_uk"]
    videos[live[:10]] = [main["id"], live]

body = json.dumps(dict(sorted(videos.items())), indent=1)
open(OUT, "w").write(f"""// Made by social-robot/tools/make_live_js.py. Do not edit by hand.
// Turns an episode into a YouTube link once it has gone live.
(() => {{
  const videos = {body};
  const now = new Date();
  const link = (id, text) => {{
    const a = document.createElement('a');
    a.href = 'https://www.youtube.com/watch?v=' + id;
    a.textContent = text;
    a.target = '_blank';
    a.rel = 'noopener';
    return a;
  }};
  document.querySelectorAll('time[datetime]').forEach((t) => {{
    const v = videos[t.getAttribute('datetime')];
    if (!v || now < new Date(v[1])) return;
    const card = t.closest('.eps li');
    const row = t.closest('table.index tbody tr');
    const head = card ? card.querySelector('h3') : row ? row.querySelector('th') : null;
    if (!head || head.querySelector('a')) return;
    if (card) {{
      const img = card.querySelector('img');
      if (!img || img.closest('a')) return;
      const a = link(v[0], '');
      a.className = 'eps__watch';
      a.setAttribute('aria-label', 'Watch ' + head.textContent + ' on YouTube (opens in a new tab)');
      img.replaceWith(a);
      const play = document.createElement('span');
      play.className = 'eps__play';
      play.setAttribute('aria-hidden', 'true');
      a.append(img, play);
      return;
    }}
    const a = link(v[0], head.textContent);
    a.title = 'Opens YouTube in a new tab';
    head.textContent = '';
    head.append(a);
  }});
}})();
""")
print(f"Wrote {OUT} with {len(videos)} episodes")
