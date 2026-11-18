"""Find the real brand artwork and place it honestly.

The word logo is the title: it goes on the cover and the title page and is
never retyped in another typeface. The icon is the mark: small and repeated,
on the world openers. Neither is ever stretched, recolored or tilted, and
both sit on dark. See the "The logo" section of BRAND.md.

The best available file wins. A print-resolution export is used if one has
been committed; otherwise the largest shipped logo is used and the placement
is sized so it stays at 300 dpi rather than being blown up soft.
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CACHE = os.path.join(HERE, '..', 'build', 'brand')

# Best first. Trimmed content width is what counts, not canvas size.
WORD_LOGO = [
    'store/brand/logo-wide-print.png',
    'dev/gen/out/logo/raw_wide.png',
    'dev/gen/out/logo/logo-wide.png',
    'img/logo-wide.webp',
]
ICON = [
    'store/brand/icon-print.png',
    'icons/icon-512.png',
]

PRINT_DPI = 300.0


def _first(paths):
    for rel in paths:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            return rel, p
    raise FileNotFoundError('no brand art found among: %s' % paths)


def trimmed(paths, name):
    """The artwork with its transparent margin removed, cached as PNG.

    Trimming matters because the shipped word logo sits in a much larger
    transparent canvas; placing the untrimmed file would shrink the mark and
    throw the clear space out.
    """
    os.makedirs(CACHE, exist_ok=True)
    rel, src = _first(paths)
    dest = os.path.join(CACHE, name + '.png')
    im = Image.open(src)
    if im.mode in ('RGBA', 'LA'):
        box = im.getbbox()
        if box:
            im = im.crop(box)
    else:
        im = im.convert('RGBA')
    im.save(dest, 'PNG')
    return {'rel': rel, 'path': dest, 'w': im.width, 'h': im.height}


def max_print_pt(art):
    """The widest this art may be drawn, in points, and still be 300 dpi."""
    return art['w'] / PRINT_DPI * 72.0


def fit(art, want_pt, floor_dpi=300.0):
    """Width and height in points for drawing this art.

    Never wider than `want_pt`, and never so wide that it drops below
    `floor_dpi`. Both sides scale together, so it is never stretched.
    """
    w = min(want_pt, art['w'] / floor_dpi * 72.0)
    return w, w * art['h'] / art['w']


def report():
    word = trimmed(WORD_LOGO, 'wordlogo')
    icon = trimmed(ICON, 'icon')
    print('word logo: %s  %dx%d  -> up to %.2f in at 300 dpi'
          % (word['rel'], word['w'], word['h'], max_print_pt(word) / 72))
    print('icon:      %s  %dx%d  -> up to %.2f in at 300 dpi'
          % (icon['rel'], icon['w'], icon['h'], max_print_pt(icon) / 72))
    return word, icon


if __name__ == '__main__':
    report()
