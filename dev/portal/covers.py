"""Build the cover pictures each portal asks for at submission.

CrazyGames wants three covers (landscape 1920x1080, portrait 800x1200, square
800x800) and allows the game's title on them and nothing else. Poki wants a
full-bleed square of at least 628x628 and asks for no text at all.

The key art is a frame from one of the game's own monster clips with a hand of
cards laid over it, so the picture says "cards" and "monsters" at a glance.

  python dev/portal/covers.py
"""
import pathlib, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONTS = ROOT / "dev" / "gen" / "fonts"
OUT = ROOT / "store" / "portal"

GOLD, CREAM, INK, RED = (242, 182, 50), (255, 245, 222), (8, 6, 5), (182, 26, 32)
# The clip each cover is cut from, and the second to take the frame at.
HERO_CLIP, HERO_AT = "balrog_idle", 2.0
SQUARE_CLIP, SQUARE_AT = "troll_idle", 2.0

# A full house of aces: rich to look at and true to how the game scores.
HAND = [("A", "spade"), ("A", "heart"), ("A", "diamond"), ("K", "club"), ("K", "heart")]


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


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


def frame(clip, at, size):
    """One frame of a monster clip, scaled to cover `size` and sharpened a
    little, since a portrait cover asks for more pixels than the clip has."""
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
    return im.crop(((im.width - tw) // 2, (im.height - th) // 2,
                    (im.width - tw) // 2 + tw, (im.height - th) // 2 + th))


def shade(im, top=0.0, bottom=0.78, start=0.45):
    """Darken towards the bottom so the title has something quiet to sit on."""
    w, h = im.size
    g = Image.new("L", (1, h))
    for y in range(h):
        t = max(0.0, (y / h - start) / (1 - start))
        g.putpixel((0, y), int(255 * (top + (bottom - top) * t * t)))
    veil = Image.new("RGB", (w, h), (6, 4, 3))
    return Image.composite(veil, im, g.resize((w, h)))


def card(w, rank, suit):
    """One playing card, drawn the way the game draws it."""
    h = round(w * 1.42)
    pad = max(2, round(w * 0.05))
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = round(w * 0.1)
    d.rounded_rectangle([pad, pad, pad + w, pad + h], r, fill=(10, 8, 6, 170))
    d.rounded_rectangle([pad, pad, pad + w - 2, pad + h - 2], r,
                        fill=CREAM, outline=(28, 20, 14), width=max(2, round(w * 0.035)))
    col = RED if suit in ("heart", "diamond") else (18, 14, 11)
    # Corner rank and one big suit mark, nothing else: at the size a portal
    # shows a cover, a second small pip only smudges into the letter.
    f1 = font("oswald.ttf", round(w * 0.40))
    d.text((pad + w * 0.21, pad + h * 0.15), rank, font=f1, fill=col, anchor="mm")
    big = pip(suit, round(w * 0.54), col)
    im.alpha_composite(big, (round(pad + w * 0.55 - big.width / 2),
                             round(pad + h * 0.63 - big.height / 2)))
    return im


def fan(im, cx, cy, cw, spread=13, step=None):
    """Lay the hand across the picture in a shallow arc."""
    step = step if step is not None else cw * 1.02
    n = len(HAND)
    for i, (rank, suit) in enumerate(HAND):
        c = card(cw, rank, suit)
        a = (i - (n - 1) / 2)
        c = c.rotate(-a * spread, Image.BICUBIC, expand=True)
        x = round(cx + a * step - c.width / 2)
        y = round(cy + abs(a) * cw * 0.09 - c.height / 2)
        im.alpha_composite(c, (x, y))
    return im


def title(im, cx, cy, size):
    d = ImageDraw.Draw(im)
    f = font("germania.ttf", size)
    for line, dy in (("AXES", -size * 0.46), ("& ACES", size * 0.46)):
        d.text((cx, cy + dy), line, font=f, fill=GOLD, anchor="mm",
               stroke_width=max(4, round(size * 0.09)), stroke_fill=INK)
    return im


def landscape():
    im = shade(frame(HERO_CLIP, HERO_AT, (1920, 1080)), bottom=0.80, start=0.34).convert("RGBA")
    fan(im, 1395, 800, 185, spread=11)
    title(im, 560, 790, 190)
    return im.convert("RGB")


def portrait():
    im = shade(frame(HERO_CLIP, HERO_AT, (800, 1200)), bottom=0.84, start=0.42).convert("RGBA")
    fan(im, 400, 780, 122, spread=12)
    title(im, 400, 1030, 150)
    return im.convert("RGB")


def square(text=True, size=800):
    im = shade(frame(SQUARE_CLIP, SQUARE_AT, (size, size)),
               bottom=0.80 if text else 0.30, start=0.40).convert("RGBA")
    k = size / 800
    fan(im, round(400 * k), round(470 * k), round(116 * k), spread=12)
    if text:
        title(im, round(400 * k), round(672 * k), round(126 * k))
    return im.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("crazygames-cover-landscape-1920x1080.jpg", landscape()),
        ("crazygames-cover-portrait-800x1200.jpg", portrait()),
        ("crazygames-cover-square-800x800.jpg", square(True)),
        ("poki-thumbnail-square-1024x1024.jpg", square(False, 1024)),
    ]
    for name, im in jobs:
        p = OUT / name
        im.save(p, quality=92, subsampling=0, optimize=True)
        print(f"  {name:<45} {im.size[0]}x{im.size[1]}  {p.stat().st_size/1024:>6.0f} KB")


main()
