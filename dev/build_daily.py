"""Build daily.html, the Guess the Monster puzzle.
Run from anywhere:  python dev/build_daily.py

dev/daily.html is a whole page of its own (unlike dev/game.html, which has no
head of its own). All this does is read the monster roster back out of the
game and drop it into the page, so the puzzle can never name a monster the
game does not have.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "gen"))
os.chdir(os.path.join(HERE, ".."))

from daily_roster import roster  # noqa: E402

MARK = "/*ROSTER*/"


def build(out="daily.html"):
    rows = roster()
    data = [{"s": r["slug"], "n": r["name"], "w": r["world"], "a": r["area"],
             "p": r["place"], "b": r["boss"], "t": r["pat"]} for r in rows]
    # short keys keep the page small; the page reads them under real names
    js = "[" + ",".join(
        '{slug:%s,name:%s,world:%s,area:%s,place:%s,boss:%d,pat:%s}' % (
            json.dumps(d["s"]), json.dumps(d["n"]), json.dumps(d["w"]),
            json.dumps(d["a"]), json.dumps(d["p"]), d["b"], json.dumps(d["t"]))
        for d in data) + "]"

    page = open("dev/daily.html", encoding="utf-8").read()
    a = page.index(MARK)
    b = page.index(MARK, a + len(MARK))
    page = page[:a + len(MARK)] + js + page[b:]
    open(out, "w", encoding="utf-8").write(page)
    print("built %s with %d monsters" % (out, len(rows)))
    return out


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "daily.html")
