"""Square opening and closing cards for the promo video."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..', '..')
F = os.path.join(HERE, 'fonts')
OUT = os.path.join(HERE, 'out')
S = 1080
GOLD, CREAM, TEAL, INK = (255, 211, 92), (243, 230, 200), (127, 227, 212), (10, 7, 5)


def font(n, s):
    return ImageFont.truetype(os.path.join(F, n), s)


def art(n):
    return Image.open(os.path.join(ROOT, 'art', n)).convert('RGBA')


def stroked(d, xy, t, f, fill, w=7):
    d.text(xy, t, font=f, fill=fill, anchor='mm', stroke_width=w, stroke_fill=(0, 0, 0))


def base(scene, monster, mh=1.0, dim=250):
    img = Image.new('RGB', (S, S), INK)
    bg = art(scene)
    r = max(S / bg.width, S / bg.height)
    bg = bg.resize((int(bg.width * r), int(bg.height * r)), Image.LANCZOS)
    img.paste(bg.convert('RGB'), ((S - bg.width) // 2, (S - bg.height) // 2))
    if monster:
        m = art(monster)
        k = (S * mh) / m.height
        m = m.resize((int(m.width * k), int(m.height * k)), Image.LANCZOS)
        img.paste(m, ((S - m.width) // 2, S - m.height + 30), m)
    sh = Image.new('L', (S, S), 0)
    sd = ImageDraw.Draw(sh)
    for i in range(60):
        k = i / 59
        sd.ellipse([S/2 - (250 + k*560), S/2 - (250 + k*560),
                    S/2 + (250 + k*560), S/2 + (250 + k*560)], fill=int(dim * (1 - k) ** .8))
    img.paste(Image.new('RGB', (S, S), INK), (0, 0), sh.filter(ImageFilter.GaussianBlur(50)))
    return img


# ---------- opening ----------
img = base('bg_castle.webp', 'dragon.webp', 1.02, 245)
d = ImageDraw.Draw(img)
d.text((S//2, 250), 'A  D A R K  C O M I C  C A R D  A D V E N T U R E', font=font('oswald.ttf', 27),
       fill=TEAL, anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0))
g = font('germania.ttf', 150)
stroked(d, (S//2, 370), 'Axes', g, GOLD, 9)
stroked(d, (S//2, 490), '& Aces', g, GOLD, 9)
stroked(d, (S//2, 600), 'Fight monsters', font('germania.ttf', 58), (255, 255, 255), 6)
stroked(d, (S//2, 665), 'with poker hands.', font('germania.ttf', 58), (255, 255, 255), 6)

CARDS = [('10', '♠', 0), ('J', '♥', 1), ('Q', '♠', 0), ('K', '♦', 1), ('A', '♠', 2)]
cw, ch, gap = 92, 130, 14
x0 = S//2 - (len(CARDS) * cw + (len(CARDS) - 1) * gap) // 2
rf, sf, pf = font('oswald.ttf', 32), font('suits.ttf', 28), font('suits.ttf', 50)
for i, (rank, suit, kind) in enumerate(CARDS):
    c = Image.new('RGBA', (cw + 24, ch + 24), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    face = (255, 233, 160) if kind == 2 else (255, 250, 240)
    cd.rounded_rectangle([12, 12, cw + 12, ch + 12], 13, fill=(0, 0, 0))
    cd.rounded_rectangle([7, 7, cw + 7, ch + 7], 13, fill=face, outline=(0, 0, 0), width=4)
    ink = (200, 22, 29) if kind == 1 else (20, 16, 14)
    cd.text((18, 14), rank, font=rf, fill=ink)
    cd.text((20, 46), suit, font=sf, fill=ink)
    cd.text((cw // 2 + 10, ch // 2 + 26), suit, font=pf, fill=ink, anchor='mm')
    rot = [-8, -4, 0, 4, 8][i]
    c = c.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.paste(c, (x0 + i * (cw + gap) - 12, 730 + (8 if abs(rot) == 8 else 0)), c)
img.save(os.path.join(OUT, 'card_square.jpg'), 'JPEG', quality=92)

# ---------- closing ----------
img = base('bg_w10_3.webp', 'demonking.webp', 1.0, 252)
d = ImageDraw.Draw(img)
stroked(d, (S//2, 300), '168 monsters.', font('germania.ttf', 70), (255, 255, 255), 7)
stroked(d, (S//2, 380), '10 quests.', font('germania.ttf', 70), (255, 255, 255), 7)
d.text((S//2, 470), 'F R E E  T O  P L A Y   ·   N O  D O W N L O A D', font=font('oswald.ttf', 26),
       fill=CREAM, anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0))
stroked(d, (S//2, 600), 'AxesAndAces', font('germania.ttf', 86), GOLD, 8)
stroked(d, (S//2, 690), '.com', font('germania.ttf', 86), GOLD, 8)
img.save(os.path.join(OUT, 'card_end.jpg'), 'JPEG', quality=92)
print('square cards written')
