"""Write the Monster Solitaire share pages under b/.

  python dev/gen/slbragpages.py

A brag picture is saved to the player's phone, so what actually gets shared is
a link. These are the pages that link points at: Open Graph tags so the chat
app shows the picture and the words, and then an immediate redirect to the
game. Each one carries its own ref, which is the only way to tell afterwards
which brag brought somebody in.

sol_ keys, so they can never collide with the card game's ach_* pages or
Monster Farkle's farkle_* ones, and every one of them lands on
solitaire.html rather than the front page.

Re-runnable: it overwrites rather than piling up.
"""
import html, io, os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SITE = "https://axesandaces.com/"
GAME = SITE + "solitaire.html"

# key -> (title, description). The description is what a chat app shows under
# the picture, so it says what the game is rather than repeating the title.
PAGES = {
    "sol_run":    ("My longest run yet",
                   "Monster Solitaire: every card you clear without touching the deck makes the blow heavier."),
    "sol_boss":   ("I brought the boss down",
                   "Monster Solitaire: three peaks of cards, and something waiting behind them."),
    "sol_level":  ("I reached a new level",
                   "Monster Solitaire: three peaks of cards, and something waiting behind them."),
    "sol_fallen": ("How far I got before I fell",
                   "Monster Solitaire: three peaks of cards, and something waiting behind them."),
    "sol_daily":  ("My score on today's reading",
                   "Monster Solitaire: everybody gets the same cards today. Free in your browser."),
    "sol":        ("Monster Solitaire",
                   "Three peaks of cards, and something waiting behind them. Free in your browser."),
}

os.makedirs("b", exist_ok=True)
made = []
for key, (title, desc) in PAGES.items():
    t, d = html.escape(title), html.escape(desc)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{t} &middot; Monster Solitaire</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website"><meta property="og:site_name" content="Monster Solitaire">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:image" content="{SITE}b/sol.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{SITE}b/{key}.html"><meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{GAME}">
<script>location.replace("{GAME}"+(location.search||"?")+(location.search?"&":"")+"ref={key}");</script>
<noscript><meta http-equiv="refresh" content="0;url={GAME}?ref={key}"></noscript>
<style>body{{background:#14100d;color:#f3e6c8;font:18px system-ui;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#f2b632}}</style></head>
<body><p>Loading <a href="{GAME}">Monster Solitaire</a>...</p></body></html>'''
    io.open(f"b/{key}.html", "w", encoding="utf-8", newline="\n").write(page)
    made.append(key)

print(f"{len(made)} share pages: {', '.join(sorted(made))}")
print("they all land on", GAME)
missing = [k for k in PAGES if not os.path.exists("b/sol.jpg")]
if missing:
    print("note: b/sol.jpg does not exist yet, so a link preview has no picture")
