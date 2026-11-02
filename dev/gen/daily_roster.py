"""Pull the monster roster straight out of dev/game.html.

The daily puzzle must never drift from the game, so nothing here is typed by
hand: every monster, its picture, the quest and area it belongs to and the way
it fights are read back out of the game's own tables. If any of those tables
change shape this raises instead of quietly shipping a short roster.

Returns a list of dicts:
  slug   picture file in art/ (art/<slug>.webp)
  name   the name the player sees
  world  quest name ("The Frozen Peaks")
  area   area name ("The Snowy Pass")
  place  the game's own line for that area ("On the icy mountain trail")
  boss   1 if it guards the end of an area
  pat    its move pattern: numbers are swings, 'B' blocks, 'H' heals
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


def _src():
    with open(os.path.join(ROOT, "dev", "game.html"), encoding="utf-8") as f:
        return f.read()


def _block(s, start, opens, closes):
    """The text from `start` to the matching close of the first `opens`."""
    i = s.index(opens, s.index(start))
    depth, j = 0, i
    while j < len(s):
        if s[j] == opens:
            depth += 1
        elif s[j] == closes:
            depth -= 1
            if depth == 0:
                return s[i:j + 1]
        j += 1
    raise AssertionError("unbalanced block after " + start)


def _pat(txt):
    """pat:[1,'B',1.6]  ->  [1, 'B', 1.6]"""
    m = re.search(r"pat:\s*\[([^\]]*)\]", txt)
    if not m:
        return []
    out = []
    for p in m.group(1).split(","):
        p = p.strip()
        if not p:
            continue
        out.append(p.strip("'\"") if p[0] in "'\"" else float(p))
    return out


def roster():
    s = _src()
    rows = []

    # ---- the ten quests: one JSON line, so read it as JSON ----
    i = s.index("const WORLDS = [")
    line = s[i + len("const WORLDS = "):s.index("\n", i)].rstrip().rstrip(";")
    worlds = json.loads(line)
    assert len(worlds) == 9, "expected 9 later quests, found %d" % len(worlds)
    for w in worlds:
        for a in w["areas"]:
            for p in a["pool"]:
                rows.append(dict(slug=p["slug"], name=p["name"], world=w["name"],
                                 area=a["name"], place=a.get("place", ""), boss=0,
                                 pat=p.get("pat", [])))
            b = a.get("boss")
            if b:
                rows.append(dict(slug=b["slug"], name=b["name"], world=w["name"],
                                 area=a["name"], place=a.get("place", ""), boss=1,
                                 pat=b.get("pat", [])))

    # ---- the first quest: plain JS tables, so read those by hand ----
    areas = re.findall(r"\{name:'([^']+)',\s*icon:'<img class=\"ico\" src=\"art/i_area_",
                       _block(s, "let AREAS = [", "[", "]"))
    assert len(areas) == 4, "expected 4 starting areas, found %d" % len(areas)
    places = [p.replace("\\'", "'") for p in
              re.findall(r"'((?:[^'\\]|\\.)*)'", _block(s, "let PLACES = [", "[", "]"))]
    assert len(places) == 4, "expected 4 starting places, found %d" % len(places)

    art = dict(re.findall(r"'([^']+)':'([^']+)'", _block(s, "const ART = {", "{", "}")))
    pools = _block(s, "let POOLS = [", "[", "]")
    # POOLS is four bracketed lists, one per area
    groups, depth, start = [], 0, None
    for k, ch in enumerate(pools[1:-1], 1):
        if ch == "[":
            if depth == 0:
                start = k
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                groups.append(pools[start:k + 1])
    assert len(groups) == 4, "expected 4 starting pools, found %d" % len(groups)

    for ai, g in enumerate(groups):
        for entry in re.findall(r"\{name:'[^']+'.*?\}", g):
            name = re.search(r"name:'([^']+)'", entry).group(1)
            slug = art.get(name)
            assert slug, "no picture for %s" % name
            rows.append(dict(slug=slug, name=name, world="The Rescue of Anna",
                             area=areas[ai], place=places[ai], boss=0, pat=_pat(entry)))

    bosses = _block(s, "bosses:[", "[", "]")
    for bi, entry in enumerate(re.findall(r"\{slug:'[^']+'.*?pat:\[[^\]]*\]\}", bosses)):
        slug = re.search(r"slug:'([^']+)'", entry).group(1)
        name = re.search(r"name:'([^']+)'", entry).group(1)
        rows.append(dict(slug=slug, name=name, world="The Rescue of Anna",
                         area=areas[bi], place=places[bi], boss=1, pat=_pat(entry)))

    # one row per picture: the game's recolored cousins share art and are left out
    seen, out = set(), []
    for r in rows:
        if r["slug"] in seen:
            continue
        seen.add(r["slug"])
        assert os.path.exists(os.path.join(ROOT, "art", r["slug"] + ".webp")), \
            "missing art for " + r["slug"]
        out.append(r)
    assert len(out) > 150, "roster came back short: %d" % len(out)
    out.sort(key=lambda r: r["name"].lower())
    return out


if __name__ == "__main__":
    rs = roster()
    print(len(rs), "monsters")
    for r in rs[:5]:
        print(r)
