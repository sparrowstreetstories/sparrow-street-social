# The post queue

One JSON file per batch (for example `2026-11.json`), each a list of posts. Claude writes these from approved episodes; Peter doesn't need to touch them.

```json
{
  "id": "2026-11-17-ep08-song-reel",          // unique
  "when": "2026-11-17 16:15",                  // UK clock time
  "title": "Episode 8 song Reel",              // for the log and the Monday report
  "type": "reel",                              // image | carousel | reel | story
  "platforms": ["instagram", "facebook"],      // and/or "pinterest"
  "media": ["2026-11/ep08-song.mp4"],          // files in docs/media/
  "caption_instagram": "…",
  "caption_facebook": "… with the YouTube link …",
  "pinterest": {"board": "Bible Memory Verses for Kids", "title": "…", "description": "…", "link": "https://youtu.be/…"},
  "test": true                                 // only for test posts: used by dry runs, never published
}
```
