"""Build b/daily.jpg, the share picture for the Guess the Monster page.

Every link to the puzzle that anyone posts shows this, so it has to say what
the thing is in one look: the word logo, the puzzle's name, and a monster
sitting in the dark the way it does on the page. The icon goes in the corner
so a thumbnail is still recognisable.

Run: python dev/gen/dailycard.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
W, H = 1200, 630
GOLD, GOLD2, CREAM, TEAL, INK = (242, 182, 50), (255, 211, 92), (243, 230, 200), (127, 227, 212), (10, 7, 5)


def font(name, size):
    return ImageFont.truetype(os.path.join(F, name), size)


def opened(*parts):
    return Image.open(os.path.join(ROOT, *parts)).convert("RGBA")


def wide(img, w):
    return img.resize((w, max(1, round(img.height * w / img.width))), Image.LANCZOS)


def stroked(d, xy, text, fnt, fill, stroke=6, anchor="ls"):
    d.text(xy, text, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def build(out=os.path.join(ROOT, "b", "daily.jpg")):
    card = Image.new("RGB", (W, H), INK)

    # the cellar, pushed right down so the words always read
    bg = opened("art", "bg_cellar.webp")
    k = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * k), round(bg.height * k)), Image.LANCZOS)
    card.paste(bg.convert("RGB"), ((W - bg.width) // 2, (H - bg.height) // 2))
    shade = Image.new("RGBA", (W, H))
    sd = ImageDraw.Draw(shade)
    for x in range(W):
        a = int(244 - 96 * min(1.0, max(0.0, (x - 560) / 640)))
        sd.line([(x, 0), (x, H)], fill=(10, 7, 5, a))
    card.paste(Image.alpha_composite(card.convert("RGBA"), shade).convert("RGB"), (0, 0))

    # ---- the monster panel, the same comic frame the page uses ----
    PX, PY, PS = 636, 62, 462
    panel = Image.new("RGBA", (PS, PS), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    for i in range(PS // 2, 0, -1):                       # radial, light in the middle
        t = 1 - i / (PS / 2)
        c = (round(18 + 40 * t), round(13 + 29 * t), round(10 + 19 * t), 255)
        pd.ellipse([PS / 2 - i * 1.35, PS / 2 - i * 1.35, PS / 2 + i * 1.35, PS / 2 + i * 1.35], fill=c)
    mon = opened("art", "dragon.webp")
    mon = wide(mon, round(PS * 0.80)) if mon.width >= mon.height else mon
    kk = min(PS * 0.80 / mon.width, PS * 0.84 / mon.height)
    mon = mon.resize((round(mon.width * kk), round(mon.height * kk)), Image.LANCZOS)
    sil = Image.new("RGBA", mon.size, (5, 4, 3, 0))
    sil.putalpha(mon.getchannel("A"))
    # the halo is blurred on a padded canvas, or the blur squares off at the edge
    PAD = 90
    halo = Image.new("L", (mon.width + PAD * 2, mon.height + PAD * 2), 0)
    halo.paste(mon.getchannel("A"), (PAD, PAD))
    halo = halo.filter(ImageFilter.GaussianBlur(40)).point(lambda v: min(255, int(v * 1.5)))
    gl = Image.new("RGBA", halo.size, (122, 82, 26, 255))
    gl.putalpha(halo)
    mx, my = (PS - mon.width) // 2, (PS - mon.height) // 2
    panel.alpha_composite(gl, (mx - PAD, my - PAD))
    panel.alpha_composite(sil, (mx, my))
    # halftone, then the black comic border
    dots = Image.new("RGBA", (PS, PS), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    for y in range(0, PS, 6):
        for x in range(0, PS, 6):
            dd.ellipse([x, y, x + 2, y + 2], fill=(0, 0, 0, 70))
    panel.alpha_composite(dots)
    frame = Image.new("RGBA", (PS, PS), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle([0, 0, PS - 1, PS - 1], 18, outline=(0, 0, 0, 255), width=7)
    panel.alpha_composite(frame)
    rounded = Image.new("L", (PS, PS), 0)
    ImageDraw.Draw(rounded).rounded_rectangle([0, 0, PS - 1, PS - 1], 18, fill=255)
    panel.putalpha(Image.composite(panel.getchannel("A"), Image.new("L", (PS, PS), 0), rounded))
    card.paste(Image.new("RGB", (PS + 8, PS + 8), (0, 0, 0)), (PX + 8, PY + 8))
    card.paste(panel.convert("RGB"), (PX, PY), panel)

    # the gold tag in the panel's corner, as on the page
    d = ImageDraw.Draw(card)
    tf = font("oswald.ttf", 22)
    tw = d.textlength("GUESS IT", font=tf)
    d.rounded_rectangle([PX + 20, PY + 20, PX + 20 + tw + 30, PY + 64], 8, fill=GOLD, outline=(0, 0, 0), width=4)
    d.text((PX + 35, PY + 42), "GUESS IT", font=tf, fill=(26, 15, 5), anchor="lm")

    # ---- the word logo, then the puzzle's own name ----
    logo = wide(opened("img", "logo-wide.webp"), 320)
    card.paste(logo, (56, 56), logo)

    y = 56 + logo.height + 54                 # clear space under the logo
    d.text((58, y - 26), "THE DAILY PUZZLE", font=font("oswald.ttf", 23), fill=TEAL,
           anchor="ls", stroke_width=4, stroke_fill=(0, 0, 0))
    g = font("germania.ttf", 76)
    stroked(d, (56, y + 56), "Guess the", g, GOLD2, 8)
    stroked(d, (56, y + 136), "Monster", g, GOLD2, 8)
    d.text((58, y + 186), "A new one every day. Five guesses.", font=font("alegreya.ttf", 30),
           fill=CREAM, anchor="ls", stroke_width=5, stroke_fill=(0, 0, 0))

    stroked(d, (58, H - 76), "Play free at", font("germania.ttf", 34), GOLD2, 7)
    stroked(d, (56, H - 26), "AxesAndAces.com", font("germania.ttf", 60), (255, 255, 255), 9)

    # the icon in the corner, so a thumbnail is still recognisable
    icon = opened("icons", "icon-512.png").resize((74, 74), Image.LANCZOS)
    ib = Image.new("RGBA", (82, 82), (0, 0, 0, 255))
    rr = Image.new("L", (82, 82), 0)
    ImageDraw.Draw(rr).rounded_rectangle([0, 0, 81, 81], 14, fill=255)
    ib.alpha_composite(icon, (4, 4))
    ib.putalpha(rr)
    card.paste(ib.convert("RGB"), (W - 82 - 44, H - 82 - 24), ib)

    d.rectangle([0, 0, W, 11], fill=(0, 0, 0))
    d.rectangle([0, H - 12, W, H], fill=(0, 0, 0))
    card.save(out, quality=90)
    print("wrote", out)
    return out


if __name__ == "__main__":
    build()
