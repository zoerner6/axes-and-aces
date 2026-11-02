"""Pull Monster Farkle's four Google fonts into the repo so a portal build can
serve them itself. Both portals forbid calling a CDN at run time, and Poki
names Google Fonts specifically.

  python dev/portal/farkle/fonts.py     writes dev/portal/farkle/fonts/ and faces.css

The card game asks for a different five (dev/portal/fonts.py). Keep the two
bundles apart: a shared one would ship each game fonts it never draws with.
"""
import pathlib, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "fonts"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
# Only the faces dev/farkle.html actually asks for, and only the Latin
# subsets: the game is English and names are typed in Latin letters.
WANT = ("Germania+One"
        "&family=Alfa+Slab+One"
        "&family=Oswald:wght@500;600;700"
        "&family=Alegreya+Sans:wght@400;500;700;800")
KEEP = {"latin", "latin-ext"}


def get(url, binary=False):
    r = subprocess.run(["curl", "-sSL", "--max-time", "60", "-A", UA, url],
                       capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode("utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    css = get("https://fonts.googleapis.com/css2?family=%s&display=swap" % WANT)
    blocks = re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    if not blocks:
        raise SystemExit("Google Fonts returned no @font-face blocks. Check WANT.")
    out, seen = [], {}
    for subset, block in blocks:
        if subset not in KEEP:
            continue
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        if url not in seen:
            name = "f%02d.woff2" % len(seen)
            (OUT / name).write_bytes(get(url, binary=True))
            seen[url] = name
        out.append(block.replace(url, "fonts/" + seen[url]))
    faces = "\n".join(" ".join(b.split()) for b in out)
    (HERE / "faces.css").write_text(faces, encoding="utf-8")
    total = sum(p.stat().st_size for p in OUT.glob("*.woff2"))
    fams = sorted({re.search(r"font-family: '([^']+)'", b).group(1) for b in out})
    print("%d font files, %.0fKB, %d @font-face rules" % (len(seen), total / 1024, len(out)))
    print("families: " + ", ".join(fams))


main()
