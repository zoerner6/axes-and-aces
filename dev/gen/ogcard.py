"""Build the share picture.

Facebook's phone composer crops a link picture to a square, so everything that
matters sits inside the middle 630px and the sides are only scenery.
Run: python dev/gen/ogcard.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
F = os.path.join(os.path.dirname(__file__), 'fonts')
W, H = 1200, 630

GOLD, CREAM, TEAL, INK = (255, 211, 92), (243, 230, 200), (127, 227, 212), (10, 7, 5)


def font(name, size):
    return ImageFont.truetype(os.path.join(F, name), size)


def art(name):
    return Image.open(os.path.join(ROOT, 'art', name)).convert('RGBA')


def stroked(d, xy, text, fnt, fill, stroke=6, anchor='mm'):
    d.text(xy, text, font=fnt, fill=fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=(0, 0, 0))


def fit(img, box_h):
    r = box_h / img.height
    return img.resize((int(img.width * r), box_h), Image.LANCZOS)


card = Image.new('RGB', (W, H), INK)

# scenery
bg = art('bg_castle.webp')
r = max(W / bg.width, H / bg.height)
bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
card.paste(bg.convert('RGB'), ((W - bg.width) // 2, (H - bg.height) // 2))

# a monster at each edge, facing in
drg = fit(art('dragon.webp'), int(H * 1.12))
card.paste(drg, (W - drg.width + 60, H - drg.height + 30), drg)
bal = fit(art('balrog.webp'), int(H * 0.98)).transpose(Image.FLIP_LEFT_RIGHT)
faded = Image.new('RGBA', bal.size)
faded.paste(bal, (0, 0))
faded.putalpha(bal.getchannel('A').point(lambda v: int(v * .55)))
card.paste(faded, (-70, H - bal.height + 40), faded)

# darken towards the middle so the words always read
sh = Image.new('L', (W, H), 0)
sd = ImageDraw.Draw(sh)
for i in range(70):
    k = i / 69
    sd.ellipse([W/2 - (300 + k*620), H/2 - (300 + k*470),
                W/2 + (300 + k*620), H/2 + (300 + k*470)], fill=int(250 * (1 - k)**0.85))
sh = sh.filter(ImageFilter.GaussianBlur(46))
card.paste(Image.new('RGB', (W, H), INK), (0, 0), sh)
top = Image.new('L', (W, H), 0)
td = ImageDraw.Draw(top)
for y in range(H):
    v = 200 if y < 70 else (210 if y > H - 90 else 0)
    if v:
        td.line([(0, y), (W, y)], fill=int(v * (1 - abs(y - (0 if y < 70 else H)) / 120)))
card.paste(Image.new('RGB', (W, H), INK), (0, 0), top)

d = ImageDraw.Draw(card)
cx = W // 2

d.text((cx, 118), 'A  D A R K  C O M I C  C A R D  A D V E N T U R E', font=font('oswald.ttf', 21),
       fill=TEAL, anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))

g = font('germania.ttf', 128)
stroked(d, (cx, 200), 'Axes', g, GOLD, 8, 'mm')
w_axes = d.textlength('Axes', font=g)
stroked(d, (cx, 288), '& Aces', g, GOLD, 8, 'mm')

stroked(d, (cx, 364), 'Fight monsters with poker hands.', font('germania.ttf', 44), (255, 255, 255), 5, 'mm')

# a poker hand across the middle
CARDS = [('10', '♠', 0), ('J', '♥', 1), ('Q', '♠', 0), ('K', '♦', 1), ('A', '♠', 2)]
cw, ch, gap = 64, 90, 10
total = len(CARDS) * cw + (len(CARDS) - 1) * gap
x0 = cx - total // 2
rank_f = font('oswald.ttf', 22)
suit_sm, pip_f = font('suits.ttf', 20), font('suits.ttf', 34)
for i, (rank, suit, kind) in enumerate(CARDS):
    c = Image.new('RGBA', (cw + 16, ch + 16), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    face = (255, 233, 160) if kind == 2 else (255, 250, 240)
    cd.rounded_rectangle([8, 8, cw + 8, ch + 8], 9, fill=(0, 0, 0))
    cd.rounded_rectangle([5, 5, cw + 5, ch + 5], 9, fill=face, outline=(0, 0, 0), width=3)
    ink = (200, 22, 29) if kind == 1 else (20, 16, 14)
    cd.text((13, 11), rank, font=rank_f, fill=ink)
    cd.text((14, 31), suit, font=suit_sm, fill=ink)
    cd.text((cw // 2 + 8, ch // 2 + 18), suit, font=pip_f, fill=ink, anchor='mm')
    rot = [-7, -3, 0, 3, 7][i]
    c = c.rotate(rot, resample=Image.BICUBIC, expand=True)
    dy = 6 if abs(rot) == 7 else 0
    card.paste(c, (x0 + i * (cw + gap) - 8, 404 + dy), c)

d.text((cx, 548), 'F R E E  T O  P L A Y   ·   N O  D O W N L O A D', font=font('oswald.ttf', 18),
       fill=CREAM, anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
stroked(d, (cx, 590), 'AxesAndAces.com', font('germania.ttf', 42), GOLD, 5, 'mm')

out = os.path.join(ROOT, 'b', 'game.jpg')
card.save(out, 'JPEG', quality=90, optimize=True)
print('wrote', out, card.size)

# prove the square crop keeps everything
sq = card.crop(((W - H) // 2, 0, (W + H) // 2, H))
sq.save(os.path.join(os.path.dirname(__file__), 'out', 'og_square_check.jpg'), 'JPEG', quality=88)
print('square-crop check written')
