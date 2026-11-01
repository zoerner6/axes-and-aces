"""The cover image for the store page (itch wants 630x500 or larger)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'fonts')
PANELS = os.path.join(HERE, '..', 'build', 'panels')
DIST = os.path.join(HERE, '..', 'dist')

W, H = 1260, 1000
SOOT = (20, 16, 13)
BRIGHT = (255, 211, 92)
GOLD = (242, 182, 50)
PARCH = (243, 230, 200)
CRIMSON = (200, 36, 31)
MUTED = (150, 130, 100)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def centered(d, y, text, f, fill):
    w = d.textbbox((0, 0), text, font=f)[2]
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def main():
    os.makedirs(DIST, exist_ok=True)
    im = Image.new('RGB', (W, H), SOOT)

    # The art has to leave room for a title block above and a strapline below,
    # so it is sized to the gap between them rather than to the full width.
    art = Image.open(os.path.join(PANELS, 'demonking_boss.jpg')).convert('RGB')
    top, art_h = 196, 596
    art_w = int(art_h * art.width / art.height)
    art = art.resize((art_w, art_h), Image.LANCZOS)
    ax = (W - art_w) // 2
    im.paste(art, (ax, top))

    fade_h = 80
    fade = Image.new('RGBA', (art_w, fade_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(fade_h):
        fd.line([(0, i), (art_w, i)],
                fill=(20, 16, 13, 255 - int(255 * i / fade_h)))
    im.paste(fade, (ax, top), fade)
    flip = fade.transpose(Image.FLIP_TOP_BOTTOM)
    im.paste(flip, (ax, top + art_h - fade_h), flip)

    d = ImageDraw.Draw(im)
    centered(d, 34, 'AXES & ACES', font('germania.ttf', 104), BRIGHT)
    centered(d, 142, 'MONSTER MANUAL', font('germania.ttf', 58), GOLD)

    y = top + art_h + 22                      # 858
    d.rectangle([90, y, W - 90, y + 5], fill=CRIMSON)
    centered(d, y + 22, '168 monsters. Ten worlds.',
             font('germania.ttf', 48), PARCH)
    centered(d, y + 86, 'FULL 5E STAT BLOCKS AND ART FOR EVERY ONE',
             font('oswald.ttf', 23), GOLD)
    centered(d, H - 36, 'Contains AI-generated content',
             font('AlegreyaSans-Regular.ttf', 20), MUTED)

    out = os.path.join(DIST, 'cover-itch.png')
    im.save(out, 'PNG', optimize=True)
    print('store cover: %s (%dx%d, %.0f KB)'
          % (os.path.abspath(out), W, H, os.path.getsize(out) / 1024))


if __name__ == '__main__':
    main()
