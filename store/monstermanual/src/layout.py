"""Page furniture: fonts, colors, text measuring and the stat block renderer.

Everything here measures first and draws second, so an entry can be fitted to
a page before a mark is made on it.
"""
import os
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, '..', 'fonts')

# ---- brand palette (BRAND.md) ----
SOOT = HexColor('#14100d')
LEATHER = HexColor('#1b1410')
INK = HexColor('#16100d')
GOLD = HexColor('#f2b632')
BRIGHT = HexColor('#ffd35c')
PARCH = HexColor('#f3e6c8')
PARCH_D = HexColor('#e7d6b2')
CRIMSON = HexColor('#c8241f')
GREEN = HexColor('#3fae4a')
TEAL = HexColor('#7fe3d8')
PURPLE = HexColor('#a63de0')
MUTED = HexColor('#6b5b44')

TITLE_F = 'Germania'
LABEL_F = 'Oswald'
BODY_F = 'Body'
BODY_I = 'BodyIt'
BODY_B = 'BodyBold'
BODY_BI = 'BodyBoldIt'


def register():
    pairs = [
        (TITLE_F, 'germania.ttf'),
        (LABEL_F, 'oswald.ttf'),
        (BODY_F, 'AlegreyaSans-Regular.ttf'),
        (BODY_I, 'AlegreyaSans-Italic.ttf'),
        (BODY_B, 'AlegreyaSans-Bold.ttf'),
        (BODY_BI, 'AlegreyaSans-BoldItalic.ttf'),
    ]
    for name, f in pairs:
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, f)))
    pdfmetrics.registerFontFamily(BODY_F, normal=BODY_F, bold=BODY_B,
                                  italic=BODY_I, boldItalic=BODY_BI)


def wrap(text, font, size, width):
    """Greedy wrap. Returns a list of lines."""
    out = []
    for para in text.split('\n'):
        if not para.strip():
            out.append('')
            continue
        words, line = para.split(), ''
        for w in words:
            trial = (line + ' ' + w).strip()
            if pdfmetrics.stringWidth(trial, font, size) <= width or not line:
                line = trial
            else:
                out.append(line)
                line = w
        if line:
            out.append(line)
    return out


def para_height(text, font, size, width, leading):
    return len(wrap(text, font, size, width)) * leading


def draw_para(c, text, x, y, font, size, width, leading, color=INK):
    """Draw wrapped text with its top at y. Returns the new y."""
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap(text, font, size, width):
        y -= leading
        if line:
            c.drawString(x, y, line)
    return y


def draw_rich(c, runs, x, y, size, width, leading, color=INK):
    """Draw a line built of (text, font) runs, wrapping across the width.

    Used for a trait, where the name is bold and the rest is not.
    """
    c.setFillColor(color)
    cx, first = x, True
    words = []
    for text, font in runs:
        for i, w in enumerate(text.split(' ')):
            if w:
                words.append((w, font))
    y -= leading
    for w, font in words:
        wd = pdfmetrics.stringWidth(w + ' ', font, size)
        if cx + wd > x + width and not first:
            y -= leading
            cx = x
        c.setFont(font, size)
        c.drawString(cx, y, w)
        cx += wd
        first = False
    return y


def rich_height(runs, size, width, leading):
    """How tall draw_rich will be, measured the same way it draws."""
    words = [(w, f) for t, f in runs for w in t.split(' ') if w]
    cx, lines, first = 0.0, 1, True
    for w, font in words:
        wd = pdfmetrics.stringWidth(w + ' ', font, size)
        if cx + wd > width and not first:
            lines += 1
            cx = 0.0
        cx += wd
        first = False
    return lines * leading
