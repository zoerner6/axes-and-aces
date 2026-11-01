"""Turn the generated Monster Farkle brand art into the files the game ships.

  python dev/gen/fkbrand.py [folder]        (default: dev/gen/brand)

The two masters are tracked in dev/gen/brand/ rather than under dev/gen/out/,
which is gitignored - the icons can then be re-cut at any size later without
paying to generate the art again. Both came out of the image generator at
1254x1254:

  dice-prop.png    the painted dice, transparent background, for the word logo
  farkle-icon.png  the square mark: an Ace of Hearts behind three dice

This trims, resizes and writes them where the game and the manifest look for
them. Re-runnable: it overwrites rather than piling up.

Monster Farkle gets its own icon on purpose. BRAND.md: a sister game is family,
not a copy, so it is built from its own object - dice - sitting with the Ace
the way the axe does in Axes & Aces. The Axes & Aces emblem still appears in
the game, quietly, as the "same people made this" mark.
"""
import os, sys
from PIL import Image

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
src = sys.argv[1] if len(sys.argv) > 1 else "dev/gen/brand"

def trim(im, pad=0.02):
    """Crop to what is actually painted, then give it a little air."""
    box = im.getchannel("A").getbbox() if im.mode == "RGBA" else im.getbbox()
    if box:
        im = im.crop(box)
    if pad:
        w, h = im.size
        p = int(max(w, h) * pad)
        out = Image.new("RGBA", (w + p * 2, h + p * 2), (0, 0, 0, 0))
        out.paste(im, (p, p))
        im = out
    return im

def square(im):
    """Centre on a transparent square, so nothing is ever stretched."""
    s = max(im.size)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    return out

os.makedirs("img", exist_ok=True)
os.makedirs("icons", exist_ok=True)
made = []

# ---- the painted dice, for the word logo ----
dice = Image.open(os.path.join(src, "dice-prop.png")).convert("RGBA")
dice = square(trim(dice))
dice.resize((560, 560), Image.LANCZOS).save("img/farkle-dice.webp", "WEBP", quality=92, method=6)
made.append("img/farkle-dice.webp")

# ---- the square mark ----
icon = Image.open(os.path.join(src, "farkle-icon.png")).convert("RGBA")
for size in (512, 192, 180):
    icon.resize((size, size), Image.LANCZOS).save(f"icons/farkle-{size}.png", "PNG", optimize=True)
    made.append(f"icons/farkle-{size}.png")

# A maskable icon is cropped to a circle by Android, so the mark has to sit
# inside the middle 80% or the launcher cuts its corners off.
SAFE = 0.78
# Take the padding colour from the art's own corner rather than assuming soot
# black: the generator's ground is nearer pure black, and the two side by side
# left a visible seam around the safe zone.
ground = icon.convert("RGB").getpixel((4, 4))
m = Image.new("RGBA", (512, 512), ground + (255,))
inner = icon.resize((int(512 * SAFE), int(512 * SAFE)), Image.LANCZOS)
m.paste(inner, ((512 - inner.width) // 2, (512 - inner.height) // 2), inner)
m.save("icons/farkle-maskable-512.png", "PNG", optimize=True)
made.append("icons/farkle-maskable-512.png")

# ---- the emblem, for sitting inline beside a line of text ----
em = icon.resize((88, 88), Image.LANCZOS)
em.convert("RGB").save("img/farkle-emblem.webp", "WEBP", quality=90, method=6)
made.append("img/farkle-emblem.webp")

for f in made:
    print(f"{f}  {os.path.getsize(f):,} bytes")
