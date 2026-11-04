"""Build the cover pictures each portal asks for at submission.

CrazyGames want three covers (landscape 1920x1080, portrait 800x1200, square
800x800) and allow the game's title on them and nothing else. Poki want a
full-bleed square of at least 628x628 and ask for no text at all.

The key art is a frame from one of the game's own monster clips with a hand of
cards over it, so the picture says "cards" and "monsters" at a glance.

The title is the word logo itself, never retyped: BRAND.md is explicit that the
word logo is the title and that nothing else should stand in for it. Poki's
cover carries the icon instead, since they do not want lettering.

  python dev/portal/covers.py
"""
import pathlib, subprocess
from PIL import Image, ImageDraw, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "store" / "portal"

SOOT = (20, 16, 13)           # #14100d, the ground everything sits on
RED = (182, 26, 32)
CREAM = (255, 245, 222)

WORDMARK = ROOT / "dev" / "gen" / "out" / "logo" / "logo-wide.png"
FALLBACK_WORDMARK = ROOT / "img" / "logo-wide.webp"
ICON = ROOT / "icons" / "icon-512.png"

# The clip each cover is cut from, and the second to take the frame at.
HERO_CLIP, HERO_AT = "balrog_idle", 2.0
SQUARE_CLIP, SQUARE_AT = "troll_idle", 2.0

# A full house of aces: rich to look at and true to how the game scores.
HAND = [("A", "spade"), ("A", "heart"), ("A", "diamond"), ("K", "club"), ("K", "heart")]

# BRAND.md: clear space all round of at least the height of the "A". Measured
# off the logo, the capitals are a little under a third of the plaque's height.
CLEAR = 0.31


def pip(suit, s, col):
    """A suit mark, drawn rather than typed: no font in the repo carries the
    four symbols, and drawn ones stay crisp at any size."""
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if suit == "diamond":
        d.polygon([(s*.5, s*.04), (s*.90, s*.5), (s*.5, s*.96), (s*.10, s*.5)], fill=col)
    elif suit == "heart":
        d.ellipse([s*.04, s*.08, s*.52, s*.58], fill=col)
        d.ellipse([s*.48, s*.08, s*.96, s*.58], fill=col)
        d.polygon([(s*.03, s*.40), (s*.97, s*.40), (s*.5, s*.97)], fill=col)
    elif suit == "spade":
        d.ellipse([s*.04, s*.34, s*.52, s*.80], fill=col)
        d.ellipse([s*.48, s*.34, s*.96, s*.80], fill=col)
        d.polygon([(s*.5, s*.03), (s*.95, s*.52), (s*.05, s*.52)], fill=col)
        d.polygon([(s*.44, s*.62), (s*.56, s*.62), (s*.66, s*.96), (s*.34, s*.96)], fill=col)
    else:  # club
        d.ellipse([s*.30, s*.03, s*.70, s*.43], fill=col)
        d.ellipse([s*.03, s*.33, s*.43, s*.73], fill=col)
        d.ellipse([s*.57, s*.33, s*.97, s*.73], fill=col)
        d.polygon([(s*.44, s*.52), (s*.56, s*.52), (s*.66, s*.96), (s*.34, s*.96)], fill=col)
    return im


def card(w, rank, suit):
    """One playing card, drawn the way the game draws it."""
    from PIL import ImageFont
    h = round(w * 1.42)
    pad = max(2, round(w * 0.05))
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = round(w * 0.1)
    d.rounded_rectangle([pad, pad, pad + w, pad + h], r, fill=(10, 8, 6, 170))
    d.rounded_rectangle([pad, pad, pad + w - 2, pad + h - 2], r,
                        fill=CREAM, outline=(28, 20, 14), width=max(2, round(w * 0.035)))
    col = RED if suit in ("heart", "diamond") else (18, 14, 11)
    f = ImageFont.truetype(str(ROOT / "dev" / "gen" / "fonts" / "oswald.ttf"), round(w * 0.40))
    d.text((pad + w * 0.21, pad + h * 0.15), rank, font=f, fill=col, anchor="mm")
    big = pip(suit, round(w * 0.54), col)
    im.alpha_composite(big, (round(pad + w * 0.55 - big.width / 2),
                             round(pad + h * 0.63 - big.height / 2)))
    return im


def fan(im, cx, cy, cw, spread=12):
    """Lay the hand across the picture in a shallow arc. Returns its box."""
    step, n = cw * 1.02, len(HAND)
    box = None
    for i, (rank, suit) in enumerate(HAND):
        c = card(cw, rank, suit)
        a = i - (n - 1) / 2
        c = c.rotate(-a * spread, Image.BICUBIC, expand=True)
        x = round(cx + a * step - c.width / 2)
        y = round(cy + abs(a) * cw * 0.09 - c.height / 2)
        im.alpha_composite(c, (x, y))
        here = (x, y, x + c.width, y + c.height)
        box = here if box is None else (min(box[0], here[0]), min(box[1], here[1]),
                                        max(box[2], here[2]), max(box[3], here[3]))
    return box


def wordmark(width):
    """The word logo, cropped to its plaque and scaled with both sides
    together. Never stretched, never retyped, never recolored."""
    src = WORDMARK if WORDMARK.exists() else FALLBACK_WORDMARK
    im = Image.open(src).convert("RGBA")
    solid = im.split()[3].point(lambda v: 255 if v > 200 else 0)
    im = im.crop(solid.getbbox())
    h = round(width * im.height / im.width)
    return im.resize((width, h), Image.LANCZOS)


def badge(size):
    """The icon as a small mark, with the corners rounded the way the app
    rounds them. Used where a portal does not want lettering."""
    ic = Image.open(ICON).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1],
                                           round(size * 0.22), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(ic, (0, 0), mask)
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(ring).rounded_rectangle(
        [1, 1, size - 2, size - 2], round(size * 0.22),
        outline=(242, 182, 50, 190), width=max(2, round(size * 0.02)))
    out.alpha_composite(ring)
    return out


def frame(clip, at, size):
    """One frame of a monster clip, scaled to cover `size`. Both sides scale
    together and the overflow is cropped, so nothing is ever stretched."""
    tmp = OUT / f".{clip}.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(at),
                    "-i", str(ROOT / "vid" / f"{clip}.mp4"), "-frames:v", "1", str(tmp)],
                   check=True)
    im = Image.open(tmp).convert("RGB")
    tmp.unlink()
    tw, th = size
    k = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    if k > 1.1:
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=3))
    base = Image.new("RGB", size, SOOT)
    base.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
    return base


def shade(im, bottom=0.78, start=0.45):
    """Darken towards the bottom so the logo has something quiet to sit on."""
    w, h = im.size
    g = Image.new("L", (1, h))
    for y in range(h):
        t = max(0.0, (y / h - start) / (1 - start))
        g.putpixel((0, y), int(255 * bottom * t * t))
    return Image.composite(Image.new("RGB", (w, h), SOOT), im, g.resize((w, h)))


def put(im, art, cx, cy):
    """Drop something centred at a point and report the box it filled."""
    x, y = round(cx - art.width / 2), round(cy - art.height / 2)
    im.alpha_composite(art, (x, y))
    return (x, y, x + art.width, y + art.height)


def check(name, canvas, logo_box, other_boxes):
    """BRAND.md asks for clear space of at least the height of the "A" all
    round the logo. Measure it rather than trusting the layout."""
    need = round(CLEAR * (logo_box[3] - logo_box[1]))
    w, h = canvas
    gaps = {"left": logo_box[0], "right": w - logo_box[2],
            "top": logo_box[1], "bottom": h - logo_box[3]}
    for b in other_boxes:
        if not b:
            continue
        overlaps_x = not (b[2] < logo_box[0] or b[0] > logo_box[2])
        overlaps_y = not (b[3] < logo_box[1] or b[1] > logo_box[3])
        if overlaps_x:                      # sits above or below the logo
            if b[3] <= logo_box[1]:
                gaps["above"] = min(gaps.get("above", 10 ** 6), logo_box[1] - b[3])
            if b[1] >= logo_box[3]:
                gaps["below"] = min(gaps.get("below", 10 ** 6), b[1] - logo_box[3])
        if overlaps_y:                      # sits beside the logo
            if b[2] <= logo_box[0]:
                gaps["beside"] = min(gaps.get("beside", 10 ** 6), logo_box[0] - b[2])
            if b[0] >= logo_box[2]:
                gaps["beside"] = min(gaps.get("beside", 10 ** 6), b[0] - logo_box[2])
        if overlaps_x and overlaps_y:
            gaps["overlapping"] = -1
    bad = {k: v for k, v in gaps.items() if v < need}
    print(f"  {name:<10} clear space needs {need}px: " +
          ("all sides OK" if not bad else f"TOO TIGHT {bad}"))


def landscape():
    im = shade(frame(HERO_CLIP, HERO_AT, (1920, 1080)), 0.80, 0.34).convert("RGBA")
    cards = fan(im, 1470, 770, 172)
    logo = put(im, wordmark(620), 440, 830)
    check("landscape", (1920, 1080), logo, [cards])
    return im.convert("RGB")


def portrait():
    im = shade(frame(HERO_CLIP, HERO_AT, (800, 1200)), 0.86, 0.40).convert("RGBA")
    cards = fan(im, 400, 660, 114)
    logo = put(im, wordmark(540), 400, 1020)
    check("portrait", (800, 1200), logo, [cards])
    return im.convert("RGB")


def square():
    im = shade(frame(SQUARE_CLIP, SQUARE_AT, (800, 800)), 0.82, 0.34).convert("RGBA")
    cards = fan(im, 400, 318, 98)
    logo = put(im, wordmark(496), 400, 634)
    check("square", (800, 800), logo, [cards])
    return im.convert("RGB")


def poki(size=1024):
    """Poki ask for no lettering, so the icon stands in for the title."""
    im = shade(frame(SQUARE_CLIP, SQUARE_AT, (size, size)), 0.42, 0.52).convert("RGBA")
    k = size / 1024
    fan(im, round(512 * k), round(585 * k), round(148 * k))
    # The mark has to survive being shown at about 190px, so it gets a
    # proper corner of its own and a soft pool of dark under it.
    b = badge(round(205 * k))
    pad = round(40 * k)
    x, y = size - b.width - pad, size - b.height - pad
    pool = Image.new("RGBA", (b.width * 2, b.height * 2), (0, 0, 0, 0))
    ImageDraw.Draw(pool).ellipse([0, 0, pool.width, pool.height], fill=(8, 6, 5, 150))
    pool = pool.filter(ImageFilter.GaussianBlur(round(26 * k)))
    im.alpha_composite(pool, (x - b.width // 2, y - b.height // 2))
    im.alpha_composite(b, (x, y))
    return im.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, im in [
        ("crazygames-cover-landscape-1920x1080.jpg", landscape()),
        ("crazygames-cover-portrait-800x1200.jpg", portrait()),
        ("crazygames-cover-square-800x800.jpg", square()),
        ("poki-thumbnail-square-1024x1024.jpg", poki()),
    ]:
        p = OUT / name
        im.save(p, quality=92, subsampling=0, optimize=True)
        print(f"  {name:<45} {im.size[0]}x{im.size[1]}  {p.stat().st_size/1024:>6.0f} KB")


main()
