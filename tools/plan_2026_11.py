"""November 2026 posts: the launch weekend (approved by Peter on 11 Nov: "Add them to the queue") and 16–30 November
(for Peter's approval). Writes the robot's queue files and a readable approval sheet from the same list, so they can't differ.

    python3 tools/plan_2026_11.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YT = "https://www.youtube.com/@SparrowStreetStories"
AI = "🎵 Our songs are made with AI music tools, from our own lyrics."
M = "2026-11/"

EP = {  # number: (title, one-line hook for parents, big idea, verse, reference, hashtags)
    1: ("Very Good!", "Hana thinks her drawing is \"just squiggles\"… until Nana Wren tells the very first story in the Bible.",
        "God made everything good, and God made you!", "God saw everything that he had made, and, behold, it was very good.", "Genesis 1:31", "#BibleStoriesForKids #Creation #SundaySchool"),
    13: ("Five Loaves and Two Fish", "Ezra has a whole box of cheesy stars and doesn't want to share a single one. Then Nana tells the story of a boy whose little lunch was given to Jesus.",
         "When we share what we have, God can do amazing things.", "God loves a cheerful giver.", "2 Corinthians 9:7", "#BibleStoriesForKids #Sharing #SundaySchool"),
    8: ("Not Too Little", "The big kids tell Hana she's \"too little\" to play trains. So Nana tells how some grown-ups once thought children were too little for Jesus… and what Jesus said next.",
        "Jesus always has time for children, including you!", "Allow the little children to come to me!", "Mark 10:14", "#BibleStoriesForKids #ChristianParenting #SundaySchool"),
    14: ("Peace Be Still", "A wild storm rattles Nana's greenhouse and Hana dives under the table. So Nana tells about the night Jesus stood up in a boat and said, \"Peace! Be still!\"",
         "Jesus is stronger than anything that scares us.", "Peace! Be still!", "Mark 4:39", "#BibleStoriesForKids #FaithAtHome #SundaySchool"),
    9: ("Who Is My Neighbour?", "Felix knocks down Ezra's cardboard lighthouse, so when Felix falls off his scooter, Ezra folds his arms. Then Nana tells the story Jesus told about a kind Samaritan.",
        "Everyone is our neighbour, so we help anyone who needs it.", "You shall love your neighbour as yourself.", "Matthew 22:39", "#BibleStoriesForKids #Kindness #SundaySchool"),
}


def release(n, when):
    t, hook, big, *_ , tags = EP[n]
    ig = f"New episode today! 🐦 Episode {n} · \"{t}\"\n\n{hook}\n\n✨ {big}\n\nWatch free on YouTube (link in bio).\n\n{tags}"
    fb = f"New episode today! 🐦 Episode {n} · \"{t}\"\n\n{hook}\n\n✨ {big}\n\nWatch free on YouTube: {YT}"
    return [
        dict(id=f"{when[:10]}-ep{n:03d}-release", when=when, title=f"Episode {n} release post", type="image", platforms=["instagram", "facebook"],
             media=[f"{M}ep{n:03d}-thumbnail.jpg"], caption_instagram=ig, caption_facebook=fb),
        dict(id=f"{when[:10]}-ep{n:03d}-story", when=when[:-2] + "20", title=f"Episode {n} 'new episode today' story", type="story", platforms=["instagram", "facebook"],
             media=[f"{M}ep{n:03d}-newepisode.jpg"]),
    ]


def song(n, when, title):
    t, _, big, verse, ref, tags = EP[n]
    cap = f"{title}\n\nSing it with your little one: \"{verse}\" {ref} (World English Bible, British Edition)\n\nFrom Sparrow Street, Episode {n}: \"{t}\"\n\n{AI}\n\n#KidsWorship #MemoryVerse #SundaySchool"
    return [
        dict(id=f"{when[:10]}-ep{n:03d}-song", when=when, title=f"Episode {n} song Reel", type="reel", platforms=["instagram", "facebook"],
             media=[f"{M}ep{n:03d}-song.mp4"], caption_instagram=cap, caption_facebook=cap + f"\n\nThe full episode: {YT}"),
        dict(id=f"{when[:10]}-ep{n:03d}-versestory", when=when[:-2] + "35", title=f"Episode {n} memory-verse story", type="story", platforms=["instagram", "facebook"],
             media=[f"{M}ep{n:03d}-verse.jpg"]),
    ]


def reel(n, when, short, text):
    t, *_, tags = EP[n]
    cap = f"{text}\n\nFrom Sparrow Street, Episode {n}: \"{t}\", gentle Bible-story cartoons for ages 3–6.\n\n{tags}"
    return [dict(id=f"{when[:10]}-ep{n:03d}-{short}", when=when, title=f"Episode {n} Reel: {short}", type="reel", platforms=["instagram", "facebook"],
                 media=[f"{M}ep{n:03d}-{short}.mp4"], caption_instagram=cap, caption_facebook=cap + f"\n\nWatch the full episode free: {YT}")]


LAUNCH = [
    dict(id="2026-11-13-launch-post", when="2026-11-13 14:15", title="Launch post", type="image", platforms=["instagram", "facebook"], media=[f"{M}launch-post.jpg"],
         caption_instagram="Sparrow Street is here 🐦\n\nAnimated Bible stories and songs for little ones aged 3–6. In Episode 1, \"Very Good!\", Hana thinks her drawing is \"just squiggles\"… until Nana Wren tells the very first story in the Bible.\n\nWatch free on YouTube (link in bio). New episodes every Tuesday and Friday.\n\n#BibleStoriesForKids #SundaySchool #ChristianParenting",
         caption_facebook=f"Sparrow Street is here 🐦\n\nAnimated Bible stories and songs for little ones aged 3–6. In Episode 1, \"Very Good!\", Hana thinks her drawing is \"just squiggles\"… until Nana Wren tells the very first story in the Bible.\n\nWatch free on YouTube: {YT}\nNew episodes every Tuesday and Friday."),
    dict(id="2026-11-13-launch-story", when="2026-11-13 14:20", title="Launch story", type="story", platforms=["instagram", "facebook"], media=[f"{M}launch-story.jpg"]),
    dict(id="2026-11-15-ep001-versecard", when="2026-11-15 10:15", title="Episode 1 memory-verse card", type="image", platforms=["instagram", "facebook"], media=[f"{M}ep001-verse.jpg"],
         caption_instagram="This week's memory verse 💛\n\"God saw everything that he had made, and, behold, it was very good.\" Genesis 1:31\n\nTry it at bedtime: say it together three times, then ask, \"What's your favourite thing God made?\"\n\n#MemoryVerse #BibleStoriesForKids #FaithAtHome",
         caption_facebook="This week's memory verse 💛\n\"God saw everything that he had made, and, behold, it was very good.\" Genesis 1:31\n\nTry it at bedtime: say it together three times, then ask, \"What's your favourite thing God made?\""),
    dict(id="2026-11-15-ep001-song", when="2026-11-15 10:30", title="Episode 1 song Reel", type="reel", platforms=["instagram", "facebook"], media=[f"{M}ep001-song.mp4"],
         caption_instagram=f"Sing it with your little one 🎵 \"God saw everything that he had made…\" Genesis 1:31 · from Sparrow Street Episode 1\n\n{AI}\n\n#KidsWorship #MemoryVerse #SundaySchool",
         caption_facebook=f"Sing it with your little one 🎵 \"God saw everything that he had made…\" Genesis 1:31 · from Sparrow Street Episode 1\n\n{AI}\n\nThe full episode: {YT}"),
]

PENDING = (
    reel(1, "2026-11-17 16:30", "glasses", "Nana, they're on your HEAD! 👓😂 Can your little one spot Nana's glasses before she does?")
    + release(13, "2026-11-17 14:15")
    + song(13, "2026-11-18 16:30", "Pass it round! 🧀⭐")
    + reel(1, "2026-11-19 16:30", "creation", "How God made the world, in 90 seconds 🌍 Count the days on your fingers with Nana Wren.")
    + release(8, "2026-11-20 14:15")
    + reel(13, "2026-11-21 10:30", "share", "Would you like a cheesy star? ⭐ Ezra learns that sharing makes everyone happier, including him.")
    + song(8, "2026-11-22 10:30", "\"Allow the little children to come to me!\" 💛")
    + reel(13, "2026-11-23 16:30", "story", "Five loaves, two fish, and more than five thousand people 🐟 Jesus feeds the crowd, in a minute (John 6).")
    + release(14, "2026-11-24 14:15")
    + reel(8, "2026-11-24 16:30", "train", "\"Choo choo?\" Everyone's welcome on this train! 🚂💛")
    + song(14, "2026-11-25 16:30", "Rock the boat… then SHH! ⛵")
    + reel(8, "2026-11-26 16:30", "story", "Jesus welcomes the children, in a minute 💛 (Mark 10)")
    + release(9, "2026-11-27 14:15")
    + reel(14, "2026-11-28 10:30", "brave", "\"I was still a little bit scared… but I did it anyway!\" 🌈 Being brave doesn't mean never feeling scared.")
    + song(9, "2026-11-29 10:30", "STOP! 🛑 Look, help, love.")
    + reel(14, "2026-11-30 16:30", "story", "Jesus calms the storm, in a minute ⛵ (Mark 4)")
)


def sheet(posts, heading):
    out = [heading, ""]
    for p in sorted(posts, key=lambda p: p["when"]):
        day = __import__("datetime").datetime.strptime(p["when"], "%Y-%m-%d %H:%M").strftime("%a %-d %b, %H:%M")
        out.append(f"### {day} · {p['title']} · {p['type']} · {' + '.join(x.capitalize() for x in p['platforms'])}")
        out.append(f"File: `{p['media'][0].split('/')[-1]}`")
        if p.get("caption_instagram"):
            out += ["", "Instagram:", "```", p["caption_instagram"], "```"]
            if p["caption_facebook"] != p["caption_instagram"]:
                out += ["Facebook:", "```", p["caption_facebook"], "```"]
        else:
            out.append("(story: picture only, no caption)")
        out.append("")
    return "\n".join(out)


def main():
    (ROOT / "queue" / "pending").mkdir(parents=True, exist_ok=True)
    (ROOT / "queue" / "2026-11-launch.json").write_text(json.dumps(LAUNCH, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "queue" / "pending" / "2026-11-16-to-30.json").write_text(json.dumps(PENDING, indent=1, ensure_ascii=False) + "\n")
    proj = ROOT.parent
    (proj / "business" / "social-posts").mkdir(exist_ok=True)
    (proj / "business" / "social-posts" / "2026-11 launch (approved).md").write_text(sheet(LAUNCH, "# Launch weekend posts · 13–15 Nov 2026 · ✅ approved by Peter 11 Nov (in the robot's queue)"))
    (proj / "business" / "social-posts" / "2026-11-16 to 30 (for approval).md").write_text(sheet(PENDING,
        f"# Posts for 16–30 November 2026 · for Peter's approval\n\n{len(PENDING)} posts: for each episode a release-day post and story, its song Reel with a memory-verse story, and its other two Shorts as Reels, each 30 minutes after the same Short goes up on YouTube. Instagram and Facebook; Pinterest stays off until Standard access. Nothing here posts until you approve it."))
    print(len(LAUNCH), "launch posts queued;", len(PENDING), "posts waiting for approval")


if __name__ == "__main__":
    main()
