"""Pull the game's five Google fonts down into the repo so a portal build can
serve them itself. Both portals forbid calling a CDN at run time.

  python dev/portal/fonts.py        writes dev/portal/fonts/ and faces.css
"""
import pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "fonts"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
# Only the faces the game actually asks for, and only the Latin subsets:
# the game is English and hero names are typed in Latin letters.
WANT = ("Germania+One"
        "&family=Vollkorn:wght@400;500;600;700;800"
        "&family=Fredoka:wght@500;600;700"
        "&family=Oswald:wght@500;600;700"
        "&family=Eczar:ital,wght@1,800")
KEEP = {"latin", "latin-ext"}

def get(url, binary=False):
    r = subprocess.run(["curl", "-sSL", "--max-time", "60", "-A", UA, url],
                       capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode("utf-8")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    css = get(f"https://fonts.googleapis.com/css2?family={WANT}&display=swap")
    blocks = re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    out, seen = [], {}
    for subset, block in blocks:
        if subset not in KEEP:
            continue
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        if url not in seen:
            name = f"f{len(seen):02d}.woff2"
            (OUT / name).write_bytes(get(url, binary=True))
            seen[url] = name
        out.append(block.replace(url, "fonts/" + seen[url]))
    faces = "\n".join(" ".join(b.split()) for b in out)
    (HERE / "faces.css").write_text(faces, encoding="utf-8")
    total = sum(p.stat().st_size for p in OUT.glob("*.woff2"))
    print(f"{len(seen)} font files, {total/1024:.0f}KB, {len(out)} @font-face rules")

main()
