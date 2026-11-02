"""Pull the ten worlds out of dev/game.html and write them into dev/solitaire.html.

  python dev/gen/slworlds.py

Same job as dev/gen/fkworlds.py, and for the same reason: the card game already
has ten worlds of areas, monster pools, bosses, place names and story beats, all
matched to art and clips that exist. Retyping any of it would be a way to get it
wrong, so it is copied - worlds two to ten straight across, and world one
rebuilt from the pieces that live loose in game.html as AREAS, POOLS and
W1.bosses.

What is NOT copied is world one's story text. The card game is poker hands at a
tavern table and the dice game is a soldier's set of knuckle bones; this is a
reading. In the Gilded Ace there is a worn deck nobody deals from, and Old Bram
lays it out in three peaks when he wants to know what is coming. That is world
one's job to explain, so its words are written here.

The result lands between the markers in dev/solitaire.html, so running this
again replaces it rather than piling up.
"""
import io, json, os, re

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
game = io.open("dev/game.html", encoding="utf-8").read()

# ---- worlds two to ten, as the card game already has them ----
worlds = json.loads(re.search(r"const WORLDS = (\[.*?\]);\n", game, re.S).group(1))

# ---- world one, from the loose pieces ----
areas1 = re.search(r"let AREAS = \[(.*?)\n\];", game, re.S).group(1)
names1 = re.findall(r"name:'([^']+)'", areas1)
pools_src = re.search(r"let POOLS = \[(.*?)\n\];", game, re.S).group(1)
mons = re.findall(r"\{name:'([^']+)',icon:'[^']*',hp:([\d.]+),atk:([\d.]+),pat:\[([^\]]*)\]\}", pools_src)
art = dict(re.findall(r"'([^']+)':'([a-z0-9]+)'", re.search(r"const ART = \{(.*?)\};", game, re.S).group(1)))


def pat(s):
    out = []
    for bit in s.split(","):
        bit = bit.strip().strip("'")
        out.append(bit if bit in ("B", "H") else float(bit))
    return out


pools1, step = [], len(mons) // 4
for a in range(4):
    chunk = mons[a * step:(a + 1) * step]
    pools1.append([{"slug": art[n], "name": n, "hp": float(h), "atk": float(k), "pat": pat(p)}
                   for n, h, k, p in chunk])

places1 = ["In the shadows of the tavern", "In the damp dark of the cellar",
           "Between the twisted trees", "In the castle's cold halls"]
bosses1 = [{"slug": "bandit", "name": "Bandit Chief", "pat": [1, "B", 1.9]},
           {"slug": "ghoul",  "name": "Cellar Ghoul", "pat": [1, "H", 1.9]},
           {"slug": "troll",  "name": "Troll King",   "pat": [1, "B", 2]},
           {"slug": "dragon", "name": "Grimstone Dragon", "pat": [1, 1, 2.1]}]

world1 = {
    "id": "w1",
    "name": "The Rescue of Anna",
    "quest": "Bring Anna home",
    "intro": [
        {"title": "The deck nobody deals from",
         "text": "Bandits take Anna out the back of the Gilded Ace. You go for your axe. Old Bram goes for the shelf behind the bar and comes back with a deck so worn the corners are round. \"I do not play with these,\" he says, and lays them out in three peaks."},
        {"title": "How to read it",
         "text": "\"The shape tells you what is waiting. Cut it away a card at a time, one rank up or one rank down, and the longer you go without stopping the harder you come out the other side. Stop, and the blow lands.\" He turns the top card over. \"Go and get her.\""}
    ],
    "areas": [
        {"name": names1[i], "place": places1[i], "pool": pools1[i], "boss": bosses1[i]}
        for i in range(4)
    ],
    "steps": [
        ["Face the goblin in the tavern", "Stop the attack"],
        ["Search the Gilded Ace", "Look for where they took Anna"],
        ["Follow the bandits to the cellar door", "They dragged Anna this way"],
        ["Go down into the Cellar", "Find Anna"],
        ["Search deeper in the Cellar", "Anna's ribbon was down here"],
        ["Find the way out of the Cellar", "The trail keeps going"],
        ["Enter the Dark Forest", "Follow Anna's trail"],
        ["Follow the footprints into the woods", "Anna's scarf points the way"],
        ["Reach the edge of the forest", "The castle must be close"],
        ["Storm Castle Grimstone", "Rescue Anna"],
        ["Climb toward the tallest tower", "You can hear Anna calling"],
        ["Face the master at the top of the tower", "Bring Anna home"]
    ],
    "story": {
        "a1": {"title": "Down the cellar stairs",
               "text": "The trapdoor is open and the stairs go down further than they should. You lay the three peaks out on the top step, read what is under them, and start down."},
        "a2": {"title": "Into the trees",
               "text": "Anna's scarf is caught on a branch at the forest edge, still warm. You deal the peaks on a flat stone. Every card comes up black."},
        "a3": {"title": "The castle gate",
               "text": "Castle Grimstone stands black against the sky. Somewhere above you, Anna is calling your name. You lay the cards out one last time and do not like the shape of them."},
        "end": [
            {"title": "Anna is safe",
             "text": "You bring Anna down the tower stairs and out through the broken gate. She does not let go of your arm the whole way home."},
            {"title": "Sir Edward",
             "text": "The Gilded Ace is full when you get back. Old Bram holds his hand out for the deck, looks it over, and puts it back in your pocket. \"They are yours now,\" he says. \"You read them better than I do.\""}
        ]
    }
}

ALL = [world1] + worlds
blob = json.dumps(ALL, separators=(",", ":"), ensure_ascii=False)

src = io.open("dev/solitaire.html", encoding="utf-8").read()
start = "/* __WORLDS_START__ */"
end = "/* __WORLDS_END__ */"
i, j = src.index(start), src.index(end)
src = src[:i] + start + "\nconst WORLDS = " + blob + ";\n" + src[j:]
io.open("dev/solitaire.html", "w", encoding="utf-8", newline="\n").write(src)

slugs = {m["slug"] for w in ALL for a in w["areas"] for m in a["pool"]} | \
        {a["boss"]["slug"] for w in ALL for a in w["areas"]}
missing = [s for s in sorted(slugs) if not os.path.exists(f"art/{s}.webp")]
print(f"{len(ALL)} worlds, {sum(len(w['areas']) for w in ALL)} areas, {len(slugs)} monsters, {len(blob)} characters")
print("missing art:", missing or "none")
missing_dead = [s for s in sorted(slugs) if not os.path.exists(f"art/dead_{s}.webp")]
print("missing fallen art:", missing_dead or "none")
