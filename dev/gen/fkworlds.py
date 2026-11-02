"""Pull the ten worlds out of dev/game.html and write them into dev/farkle.html.

  python dev/gen/fkworlds.py

The card game already has ten worlds of areas, monster pools, bosses, place
names and story beats, all matched to art and clips that exist. Retyping any of
that would be a way to get it wrong, so it is copied: WORLDS (worlds two to
ten) straight across, and world one rebuilt from the pieces that live loose in
game.html as AREAS, POOLS and W1.bosses.

What is NOT copied is the story text. A card game's words do not fit a dice
game, and the first world is where the dice have to be explained, so world
one's beats are written here.

The result lands between the markers in dev/farkle.html, so running this again
replaces it rather than piling up.
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
# each pool is a run of {name:'..',icon:'..',hp:..,atk:..,pat:[..]}
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

# World one is where the dice get explained, so its words are written here and
# not borrowed from a game about cards.
world1 = {
    "id": "w1",
    "name": "The Rescue of Anna",
    "quest": "Bring Anna home",
    "intro": [
        {"title": "A set of old bones",
         "text": "Bandits take Anna out the back of the Gilded Ace. You go for your axe and find Old Bram already holding something else: six dice, cut from a dragon's knuckles, worn smooth. \"A soldier's set,\" he says. \"Not a gambler's.\""},
        {"title": "How the dice fight",
         "text": "\"Every die you keep winds the swing up tighter. Keep pushing and the blow gets heavier. Push too far and your guard drops, and whatever you are facing gets its hit in first.\" He puts them in your hand. \"Go and get her.\""}
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
               "text": "The trapdoor is open and the stairs go down further than they should. You roll the dice once in your palm, the way Bram showed you, and start down."},
        "a2": {"title": "Into the trees",
               "text": "Anna's scarf is caught on a branch at the forest edge, still warm. Whatever is in these trees has been watching you since the treeline."},
        "a3": {"title": "The castle gate",
               "text": "Castle Grimstone stands black against the sky. Somewhere above you, Anna is calling your name. The dice are heavy in your hand."},
        "end": [
            {"title": "Anna is safe",
             "text": "You bring Anna down the tower stairs and out through the broken gate. She does not let go of your arm the whole way home."},
            {"title": "Sir Edward",
             "text": "The Gilded Ace is full when you get back. Old Bram takes the dice, looks them over, and hands them straight back. \"Keep them,\" he says. \"You will want them again.\""}
        ]
    }
}

ALL = [world1] + worlds
blob = json.dumps(ALL, separators=(",", ":"), ensure_ascii=False)

src = io.open("dev/farkle.html", encoding="utf-8").read()
start = "/* __WORLDS_START__ */"
end = "/* __WORLDS_END__ */"
i, j = src.index(start), src.index(end)
src = src[:i] + start + "\nconst WORLDS = " + blob + ";\n" + src[j:]
io.open("dev/farkle.html", "w", encoding="utf-8", newline="\n").write(src)

slugs = {m["slug"] for w in ALL for a in w["areas"] for m in a["pool"]} | \
        {a["boss"]["slug"] for w in ALL for a in w["areas"]}
missing = [s for s in sorted(slugs) if not os.path.exists(f"art/{s}.webp")]
print(f"{len(ALL)} worlds, {sum(len(w['areas']) for w in ALL)} areas, {len(slugs)} monsters, {len(blob)} characters")
print("missing art:", missing or "none")
missing_dead = [s for s in sorted(slugs) if not os.path.exists(f"dead_{s}.webp".join(["art/", ""]))]
print("missing fallen art:", missing_dead or "none")
