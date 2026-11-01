"""Write the Monster Farkle share pages into b/.

  python dev/gen/fkbrag.py

A share page is what Facebook actually fetches when somebody posts a brag
picture: it carries the og: tags so the post shows the card, then sends the
visitor straight to the game. Keys are prefixed farkle_ so none of them can
collide with the card game's 220 pages already in b/.

The picture each page points at is the one the game draws on the player's own
device, so these pages name a fallback image that lives in b/ already.
"""
import io, os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

SITE = "https://axesandaces.com/"
PAGES = {
    "farkle":        ("Monster Farkle",
                      "Six dice, one monster. Wind up the blow, or lose the lot. Free in your browser."),
    "farkle_boss":   ("I brought down the boss",
                      "Monster Farkle: six dice against a monster. Wind up the blow, or lose the lot."),
    "farkle_hit":    ("My biggest hit yet",
                      "Monster Farkle: the longer you push, the harder you hit. Free in your browser."),
    "farkle_level":  ("I leveled up in Monster Farkle",
                      "Six dice, ten worlds and a monster at every turn. Free in your browser."),
    "farkle_fallen": ("See how far I got",
                      "Monster Farkle: push your luck with six dice. Beat my run, free in your browser."),
    "farkle_daily":  ("Today's dice",
                      "Everybody gets the same dice today in Monster Farkle. Beat my score, free."),
}

TPL = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title} &middot; Monster Farkle</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website"><meta property="og:site_name" content="Monster Farkle">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}b/game.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{site}b/{key}.html"><meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{site}farkle.html">
<script>location.replace("{site}farkle.html"+(location.search||"?")+(location.search?"&":"")+"ref={key}");</script>
<noscript><meta http-equiv="refresh" content="0;url={site}farkle.html?ref={key}"></noscript>
<style>body{{background:#14100d;color:#f3e6c8;font:18px system-ui;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#f2b632}}</style></head>
<body><p>Loading <a href="{site}farkle.html">Monster Farkle</a>...</p></body></html>
"""

made = []
for key, (title, desc) in PAGES.items():
    path = f"b/{key}.html"
    io.open(path, "w", encoding="utf-8", newline="\n").write(
        TPL.format(key=key, title=title.replace('"', "&quot;"), desc=desc.replace('"', "&quot;"), site=SITE))
    made.append(path)
print(f"wrote {len(made)} share pages:", ", ".join(made))
