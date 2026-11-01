"""The cover image for the store page (itch wants 630x500 or larger)."""
import os
from PIL import Image, ImageDraw, ImageFont

import brand

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
    """Laid out top down, each block placed under the one before it, so
    nothing can land on top of the art."""
    os.makedirs(DIST, exist_ok=True)
    im = Image.new('RGB', (W, H), SOOT)
    d = ImageDraw.Draw(im)

    # The word logo is the title here too, never retyped.
    word = brand.trimmed(brand.WORD_LOGO, 'wordlogo')
    logo = Image.open(word['path']).convert('RGBA')
    lw = 560
    logo = logo.resize((lw, int(lw * logo.height / logo.width)), Image.LANCZOS)
    im.paste(logo, ((W - lw) // 2, 6), logo)
    y = 6 + logo.height + 4

    f_title = font('germania.ttf', 54)
    centered(d, y, 'MONSTER MANUAL', f_title, GOLD)
    y += d.textbbox((0, 0), 'MONSTER MANUAL', font=f_title)[3] + 18

    # Whatever is left between the title and the strapline is the art.
    strap_h = 196
    art_h = H - y - strap_h
    art = Image.open(os.path.join(PANELS, 'demonking_boss.jpg')).convert('RGB')
    art_w = int(art_h * art.width / art.height)
    if art_w > W:
        art_w, art_h = W, int(W * art.height / art.width)
    art = art.resize((art_w, art_h), Image.LANCZOS)
    ax = (W - art_w) // 2
    im.paste(art, (ax, y))

    fade_h = min(70, art_h // 4)
    fade = Image.new('RGBA', (art_w, fade_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for i in range(fade_h):
        fd.line([(0, i), (art_w, i)],
                fill=(20, 16, 13, 255 - int(255 * i / fade_h)))
    im.paste(fade, (ax, y), fade)
    flip = fade.transpose(Image.FLIP_TOP_BOTTOM)
    im.paste(flip, (ax, y + art_h - fade_h), flip)

    y += art_h + 22
    d.rectangle([90, y, W - 90, y + 5], fill=CRIMSON)
    centered(d, y + 18, '168 monsters. Ten worlds.',
             font('germania.ttf', 46), PARCH)
    centered(d, y + 84, 'FULL 5E STAT BLOCKS AND ART FOR EVERY ONE',
             font('oswald.ttf', 22), GOLD)
    centered(d, y + 130, 'Contains AI-generated content',
             font('AlegreyaSans-Regular.ttf', 19), MUTED)

    out = os.path.join(DIST, 'cover-itch.png')
    im.save(out, 'PNG', optimize=True)
    print('store cover: %s (%dx%d, %.0f KB)'
          % (os.path.abspath(out), W, H, os.path.getsize(out) / 1024))


if __name__ == '__main__':
    main()
