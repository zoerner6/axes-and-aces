"""Lay the whole book out as a PDF.

Run twice: the first pass records which page everything landed on, the second
uses those numbers to fill in the contents.
"""
import json, os, sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

import brand
import layout as L
import statblock as SB
import text as T
import engine as ENG
from engine import cr_name

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, '..', 'build')
PANELS = os.path.join(BUILD, 'panels')
DIST = os.path.join(HERE, '..', 'dist')

PW, PH = letter                     # 612 x 792 pt
M = 42.0                            # margin
CW = PW - 2 * M                     # content width 528
TOP = PH - M
BOT = M + 16                        # leave room for the folio

PANEL_W = 206.0                     # mob panel
PANEL_H = PANEL_W * 602 / 1080
GUTTER = 16.0
BLOCK_W = CW - PANEL_W - GUTTER
MIN_SLOT = 302.0                    # two mob entries to a page

# ---- print edition -------------------------------------------------------
# Amazon KDP trims 0.125 in off the top, bottom and outside edge, so a print
# interior is laid out on a larger sheet and the trim box is slid to one side
# depending on which hand the page falls on. The 42 pt margin already clears
# KDP's minimums for this page count - 0.5 in gutter, 0.375 in outside with
# bleed - so only the sheet changes, never the text block.
BLEED = 9.0                         # 0.125 in


class Book:
    def __init__(self, path, toc=None, kdp=False):
        self.kdp = kdp
        self.bleed = BLEED if kdp else 0.0
        size = (PW + self.bleed, PH + 2 * self.bleed) if kdp else letter
        self.c = canvas.Canvas(path, pagesize=size)
        self.c.setTitle(T.TITLE)
        self.c.setAuthor('Axes & Aces')
        self.c.setSubject('A 5E-compatible bestiary of 168 monsters')
        self.c.setKeywords('5e, bestiary, monsters, fifth edition, SRD')
        self.page = 1
        self.toc = toc or {}
        self.marks = {}
        self.y = TOP
        self.chapter = ''
        self.word = brand.trimmed(brand.WORD_LOGO, 'wordlogo')
        self.icon = brand.trimmed(brand.ICON, 'icon')
        self._origin()

    def _origin(self):
        """Slide the trim box so the bleed falls on the outside edge.

        A right-hand page bleeds to the right, so the trim sits flush left; a
        left-hand page is the other way round. showPage resets the matrix, so
        this is re-applied for every page.
        """
        if not self.kdp:
            return
        self.c.translate(0.0 if self.page % 2 else self.bleed, self.bleed)

    # ---- page plumbing -------------------------------------------------
    def mark(self, key):
        self.marks.setdefault(key, self.page)

    def folio(self, dark=False):
        if self.page == 1:
            return
        self.c.setFont(L.LABEL_F, 8)
        self.c.setFillColor(L.GOLD if dark else L.MUTED)
        self.c.drawCentredString(PW / 2, M - 1, str(self.page))
        if self.chapter and not dark:
            self.c.setFont(L.BODY_I, 7.5)
            self.c.setFillColor(L.MUTED)
            # 0.375 in (27 pt) clear of the trim is KDP's minimum on the
            # top edge. At +10 the cap height reached 26 pt and the previewer
            # called it.
            self.c.drawRightString(PW - M, PH - M + 4, self.chapter)

    def bg(self, color=L.PARCH):
        """Page colour, run out past the trim on every side."""
        b = self.bleed * 2
        self.c.setFillColor(color)
        self.c.rect(-b, -b, PW + 2 * b, PH + 2 * b, stroke=0, fill=1)

    def full_x(self):
        """Left edge and width of something that must reach both trim edges."""
        return -self.bleed, PW + 2 * self.bleed

    def new_page(self, dark=False):
        self.folio(dark)
        self.c.showPage()
        self.page += 1
        self._origin()
        self.bg(L.SOOT if dark else L.PARCH)
        self.y = TOP

    def space(self, need):
        """Make sure `need` points are free, starting a page if not."""
        if self.y - need < BOT:
            self.new_page()

    # ---- pieces --------------------------------------------------------
    def panel_img(self, slug, boss, x, y, w):
        p = os.path.join(PANELS, '%s_%s.jpg' % (slug, 'boss' if boss else 'mob'))
        h = w * (1088 / 1950 if boss else 602 / 1080)
        # comic panel: hard offset shadow, thick ink border (BRAND.md)
        self.c.setFillColor(L.SOOT)
        self.c.rect(x + 3, y - h - 3, w, h, stroke=0, fill=1)
        self.c.drawImage(p, x, y - h, w, h, mask=None)
        self.c.setStrokeColor(L.SOOT)
        self.c.setLineWidth(2.2)
        self.c.rect(x, y - h, w, h, stroke=1, fill=0)
        return h

    def heading(self, txt, size=20, color=L.CRIMSON, font=None):
        self.space(size + 14)
        self.c.setFont(font or L.TITLE_F, size)
        self.c.setFillColor(color)
        self.y -= size + 2
        self.c.drawString(M, self.y, txt)
        self.y -= 8

    def body(self, txt, size=10, leading=13.4, width=None, font=None,
             color=L.INK, indent=0):
        width = width or CW
        font = font or L.BODY_F
        for para in txt.split('\n\n'):
            lines = L.wrap(para, font, size, width)
            i = 0
            while i < len(lines):
                if self.y - leading < BOT:
                    self.new_page()
                self.c.setFont(font, size)
                self.c.setFillColor(color)
                self.y -= leading
                self.c.drawString(M + indent, self.y, lines[i])
                i += 1
            self.y -= leading * 0.45


# ------------------------------------------------------------------ pages
def fade_edge(c, y_edge, depth, up, x=0.0, w=PW):
    """Blend an image edge into the soot page.

    Solid at the edge and clear `depth` points in, so the picture dissolves
    into the black instead of stopping at a line. `up` fades upward from a
    bottom edge, otherwise downward from a top edge.
    """
    steps = 80
    step = depth / steps
    for i in range(steps):
        c.setFillColorRGB(0.078, 0.063, 0.051, alpha=1.0 - i / float(steps))
        y = y_edge + i * step if up else y_edge - (i + 1) * step
        c.rect(x, y, w, step + 0.6, stroke=0, fill=1)
    # The fill alpha persists in the graphics state, and the last step above
    # leaves it near zero. Images drawn afterwards would come out as ghosts.
    c.setFillAlpha(1)


def cover(bk):
    """The word logo is the title. It is never retyped in another typeface,
    and never drawn wider than the artwork can hold at 300 dpi.

    Laid out downward from the logo's real height, so a different logo file
    moves everything below it instead of colliding with it.
    """
    c = bk.c
    bk.bg(L.SOOT)

    lw, lh = brand.fit(bk.word, 400)
    ly = PH - 40 - lh
    c.drawImage(bk.word['path'], (PW - lw) / 2, ly, lw, lh, mask='auto')

    # Clear space below the logo of more than the height of its "A", then
    # this book's own name, which is type rather than artwork.
    title_base = ly - 34 - 28
    c.setFont(L.TITLE_F, 40)
    c.setFillColor(L.GOLD)
    c.drawCentredString(PW / 2, title_base, 'MONSTER MANUAL')

    img = os.path.join(PANELS, 'demonking_boss.jpg')
    ih = PW * 1088 / 1950                      # 341 pt at full bleed
    iy = title_base - 30 - ih
    fx, fw = bk.full_x()
    c.drawImage(img, fx, iy, fw, ih, mask=None)
    fade_edge(c, iy + ih, 78, up=False, x=fx, w=fw)   # top edge of the art
    fade_edge(c, iy, 78, up=True, x=fx, w=fw)         # bottom edge

    y = iy - 20
    c.setFillColor(L.CRIMSON)
    c.rect(M, y, CW, 3, stroke=0, fill=1)
    c.setFont(L.TITLE_F, 26)
    c.setFillColor(L.PARCH)
    c.drawCentredString(PW / 2, y - 33, '168 monsters. Ten worlds.')
    c.setFont(L.BODY_F, 12.5)
    c.setFillColor(L.PARCH)
    c.drawCentredString(PW / 2, y - 55, 'From the free card game at ' + T.SITE)
    c.setFont(L.LABEL_F, 11.5)
    c.setFillColor(L.GOLD)
    c.drawCentredString(PW / 2, y - 80, T.TAGLINE.upper())
    c.setFont(L.BODY_F, 8.5)
    c.setFillColor(L.MUTED)
    c.drawCentredString(PW / 2, y - 107,
                        'Contains AI-generated content. See page 3.')
    bk.new_page()


def title_page(bk):
    """The logo carries its own dark plaque, so it sits on parchment without
    the bare lettering ever touching pale paper."""
    c = bk.c
    word = bk.word
    lw, lh = brand.fit(word, 340)
    ly = PH - 150 - lh
    c.drawImage(word['path'], (PW - lw) / 2, ly, lw, lh, mask='auto')

    y = ly - 52
    c.setFont(L.TITLE_F, 34)
    c.setFillColor(L.CRIMSON)
    c.drawCentredString(PW / 2, y, 'MONSTER MANUAL')
    y -= 26
    c.setFont(L.BODY_I, 13)
    c.setFillColor(L.INK)
    c.drawCentredString(PW / 2, y, T.SUBTITLE)

    y -= 26
    c.setFillColor(L.CRIMSON)
    c.rect(PW / 2 - 110, y, 220, 1.6, stroke=0, fill=1)

    icon = bk.icon
    y -= 86
    c.drawImage(icon['path'], PW / 2 - 29, y, 58, 58, mask='auto')

    y -= 34
    c.setFont(L.LABEL_F, 11)
    c.setFillColor(L.MUTED)
    c.drawCentredString(PW / 2, y, T.TAGLINE.upper())
    c.setFont(L.BODY_F, 11)
    c.setFillColor(L.INK)
    c.drawCentredString(PW / 2, 86, 'Play the game free at ' + T.SITE)
    bk.new_page()


def legal(bk):
    bk.chapter = ''
    bk.heading(T.AI_DISCLOSURE_TITLE, 22)
    bk.body(T.AI_DISCLOSURE, 10.5, 14)
    bk.y -= 10
    bk.c.setStrokeColor(L.CRIMSON)
    bk.c.setLineWidth(1)
    bk.c.line(M, bk.y, PW - M, bk.y)
    bk.y -= 14
    bk.heading('Licence', 15)
    bk.body(T.SRD_NOTICE, 9, 12)
    bk.body(T.SRD_MODIFICATIONS, 9, 12)
    bk.body(T.COPYRIGHT, 9, 12)
    bk.body('Body text is set in Alegreya Sans and headings in Germania One '
            'and Oswald, all under the SIL Open Font Licence.', 9, 12)
    bk.new_page()


def contents(bk, worlds):
    bk.mark('contents')
    bk.heading('Contents', 26)
    bk.y -= 4
    rows = [('Introduction', 'intro')]
    rows += [(w['name'], 'world_%s' % w['id']) for w in worlds]
    rows += [('Encounters', 'app_enc'),
             ('Monsters by challenge rating', 'app_cr'),
             ('Monsters by kind', 'app_type'),
             ('Monsters by terrain', 'app_terrain'),
             ('Monsters by name', 'app_az'),
             ('All 168 at a glance', 'app_glance')]
    for i, (label, key) in enumerate(rows):
        bk.space(19)
        bk.y -= 18
        is_world = key.startswith('world_')
        bk.c.setFont(L.TITLE_F if is_world else L.BODY_B, 13 if is_world else 11)
        bk.c.setFillColor(L.CRIMSON if is_world else L.INK)
        num = '%d. ' % i if is_world else ''
        bk.c.drawString(M + (0 if is_world else 8), bk.y, num + label)
        pg = bk.toc.get(key)
        if pg:
            bk.c.setFont(L.LABEL_F, 10)
            bk.c.setFillColor(L.MUTED)
            bk.c.drawRightString(PW - M, bk.y, str(pg))
            w = pdfmetrics.stringWidth(num + label, L.TITLE_F if is_world else L.BODY_B,
                                       13 if is_world else 11)
            bk.c.setStrokeColor(L.PARCH_D)
            bk.c.setLineWidth(0.8)
            bk.c.line(M + w + 10, bk.y + 2, PW - M - 22, bk.y + 2)
    bk.new_page()


def intro(bk):
    bk.mark('intro')
    bk.chapter = 'Introduction'
    bk.heading('Introduction', 26)
    for head, bodytext in T.INTRO:
        bk.space(40)
        bk.y -= 8
        bk.heading(head, 14)
        bk.body(bodytext, 10, 13.4)
    bk.new_page()


def world_opener(bk, w, blocks):
    bk.new_page(dark=True) if bk.y != TOP else bk.bg(L.SOOT)
    bk.mark('world_%s' % w['id'])
    c = bk.c
    bs = [b for b in blocks if b['world_i'] == w['i']]
    hero = next((b for b in bs if b['boss'] and b['area_i'] == 3), bs[-1])
    img = os.path.join(PANELS, '%s_boss.jpg' % hero['slug'])
    ih = PW * 1088 / 1950
    fx, fw = bk.full_x()
    c.drawImage(img, fx, PH - ih, fw, ih + bk.bleed * 2, mask=None)
    fade_edge(c, PH - ih, 80, up=True, x=fx, w=fw)   # bottom edge of the art

    # The icon is the mark: small and repeated, one on each world opener.
    y = PH - ih - 18
    ic = 26
    c.drawImage(bk.icon['path'], M, y - 9, ic, ic, mask='auto')
    c.setFont(L.LABEL_F, 11)
    c.setFillColor(L.GOLD)
    c.drawString(M + ic + 9, y, 'WORLD %d' % (w['i'] + 1))
    y -= 42
    c.setFont(L.TITLE_F, 40)
    c.setFillColor(L.BRIGHT)
    c.drawString(M, y, w['name'])
    y -= 20
    c.setFont(L.BODY_I, 13)
    c.setFillColor(L.PARCH)
    c.drawString(M, y, 'The quest: %s' % w['quest'])

    y -= 10
    c.setFillColor(L.CRIMSON)
    c.rect(M, y, CW, 2.5, stroke=0, fill=1)
    y -= 18

    pls = sorted({b['party_level'] for b in bs})
    crs = sorted({b['cr'] for b in bs})
    c.setFont(L.LABEL_F, 9.5)
    c.setFillColor(L.GOLD)
    c.drawString(M, y, 'FOR PARTIES OF LEVEL %d-%d   ·   %d MONSTERS   ·   '
                       'CHALLENGE %s TO %s'
                 % (pls[0], pls[-1], len(bs), cr_name(crs[0]), cr_name(crs[-1])))
    y -= 22

    # Bram's note
    for line in L.wrap(T.BRAM[w['id']], L.BODY_I, 11.5, CW - 40):
        y -= 15.5
        c.setFont(L.BODY_I, 11.5)
        c.setFillColor(L.PARCH)
        c.drawString(M + 20, y, line)
    y -= 6
    c.setFont(L.BODY_F, 9.5)
    c.setFillColor(L.MUTED)
    c.drawString(M + 20, y - 8, '— Bram, who keeps the Gilded Ace')

    y -= 34
    c.setFont(L.LABEL_F, 9.5)
    c.setFillColor(L.GOLD)
    c.drawString(M, y, 'THE FOUR AREAS')
    y -= 4
    for a_i, area in enumerate(w['areas']):
        in_area = [b for b in bs if b['area_i'] == a_i]
        boss = next((b for b in in_area if b['boss']), None)
        y -= 15
        c.setFont(L.BODY_B, 10)
        c.setFillColor(L.PARCH)
        c.drawString(M + 12, y, '%d. %s' % (a_i + 1, area['name']))
        c.setFont(L.BODY_F, 9.5)
        c.setFillColor(L.MUTED)
        c.drawRightString(PW - M, y, '%d monsters, boss: %s'
                          % (len(in_area), boss['name'] if boss else '—'))
    # The opener is the only dark page in the chapter. The entries after it go
    # on parchment, or their ink-colored text would be invisible.
    bk.folio(dark=True)
    bk.c.showPage()
    bk.page += 1
    bk.bg(L.PARCH)
    bk.y = TOP
    bk.chapter = w['name']


def provenance(bk, b, x, y, width):
    c = bk.c
    c.setFont(L.LABEL_F, 7.2)
    c.setFillColor(L.CRIMSON)
    c.drawString(x, y - 7, 'FOR A LEVEL %d PARTY' % b['party_level'])
    c.setFont(L.BODY_F, 7.6)
    c.setFillColor(L.MUTED)
    y -= 17
    note = '%s · %s' % (b['world'], b['area'])
    c.drawString(x, y, note[:90])
    y -= 9
    c.drawString(x, y, 'game numbers: health ×%.2g, attack ×%.2g'
                 % (b['game_hp'], b['game_atk']))
    return y - 4


def flavor(bk, b, x, y, width):
    y = L.draw_para(bk.c, b['desc'], x, y, L.BODY_I, 9, width, 11.6, L.INK)
    y -= 5
    runs = [('How it fights. ', L.BODY_BI), (b['tactics'], L.BODY_F)]
    y = L.draw_rich(bk.c, runs, x, y, 9, width, 11.6, L.MUTED)
    return y


def mob_entry(bk, b):
    parts = SB.parts_for(b)
    bh = SB.height(parts, BLOCK_W)
    lh = PANEL_H + 30 + L.para_height(b['desc'], L.BODY_I, 9, PANEL_W, 11.6) \
        + L.rich_height([('How it fights. ', L.BODY_BI), (b['tactics'], L.BODY_F)],
                        9, PANEL_W, 11.6) + 10
    # A minimum slot so two entries always share a page evenly. Without it a
    # tall entry pushes the next one over and leaves most of a page blank.
    need = max(bh, lh, MIN_SLOT) + 14
    bk.space(need)
    bk.mark('mon_%s' % b['slug'])
    top = bk.y
    bk.panel_img(b['slug'], False, M, top, PANEL_W)
    ly = provenance(bk, b, M, top - PANEL_H - 6, PANEL_W)
    flavor(bk, b, M, ly, PANEL_W)
    SB.draw(bk.c, parts, b, M + PANEL_W + GUTTER, top, BLOCK_W)
    bk.y = top - need + 4
    bk.c.setStrokeColor(L.PARCH_D)
    bk.c.setLineWidth(1)
    bk.c.line(M, bk.y + 2, PW - M, bk.y + 2)


FLAVOR_ALLOW = 46.0     # the boss line and the two lines of flavour above


def _tallest_column(parts, colw):
    """Height of the taller of the two columns a boss block is split into."""
    total = SB.height(parts, colw)
    run, cut = 0.0, len(parts)
    for i, p in enumerate(parts):
        run += SB.height([p], colw)
        if run >= total / 2 and parts[i]['kind'] not in ('head', 'rule'):
            cut = i + 1
            break
    return max(SB.height(parts[:cut], colw), SB.height(parts[cut:], colw))


def boss_entry(bk, b):
    if bk.y < TOP - 2:
        bk.new_page()
    bk.mark('mon_%s' % b['slug'])
    c = bk.c
    top = bk.y

    # The picture gives up room before the stat block does. The Lich carries
    # eight levels of spells and the Demon King carries lair actions, and at
    # the full panel size their taller column runs off the bottom of the page.
    # Narrowing the panel keeps one boss to one page, which is the point of
    # giving it a page.
    parts = SB.parts_for(b)
    colw = (CW - 22) / 2
    need = _tallest_column(parts, colw)
    pw = CW
    while pw > CW * 0.55:
        ph = pw * (1088 / 1950)
        if (top - ph - 12 - FLAVOR_ALLOW) - BOT >= need:
            break
        pw -= 12
    ph = bk.panel_img(b['slug'], True, M + (CW - pw) / 2, top, pw)
    y = top - ph - 12

    c.setFont(L.LABEL_F, 9)
    c.setFillColor(L.CRIMSON)
    c.drawString(M, y, 'BOSS · %s · FOR A LEVEL %d PARTY'
                 % (b['area'].upper(), b['party_level']))
    y -= 8
    y = flavor(bk, b, M, y, CW)
    y -= 8

    # Split the block across two columns at the part that balances them best.
    total = SB.height(parts, colw)
    run, cut = 0.0, len(parts)
    for i, p in enumerate(parts):
        run += SB.height([p], colw)
        if run >= total / 2 and parts[i]['kind'] not in ('head', 'rule'):
            cut = i + 1
            break
    SB.draw(c, parts[:cut], b, M, y, colw)
    SB.draw(c, parts[cut:], b, M + colw + 22, y, colw)
    bk.new_page()


def appendix_cr(bk, blocks):
    bk.chapter = 'Appendix'
    bk.mark('app_cr')
    bk.heading('Monsters by challenge rating', 22)
    bk.body(T.APPENDIX_CR, 10, 13.4)
    bk.y -= 6
    for cr in sorted({b['cr'] for b in blocks}):
        rows = sorted((b for b in blocks if b['cr'] == cr), key=alpha_key)
        bk.space(26)
        bk.y -= 17
        bk.c.setFont(L.TITLE_F, 13)
        bk.c.setFillColor(L.CRIMSON)
        bk.c.drawString(M, bk.y, 'Challenge %s' % cr_name(cr))
        bk.y -= 3
        for b in rows:
            bk.space(13)
            bk.y -= 12
            bk.c.setFont(L.BODY_F, 9.5)
            bk.c.setFillColor(L.INK)
            bk.c.drawString(M + 14, bk.y, b['name'])
            bk.c.setFont(L.BODY_F, 9)
            bk.c.setFillColor(L.MUTED)
            bk.c.drawRightString(PW - M - 26, bk.y,
                                 '%s · %s' % (b['world'], b['size']))
            page_no(bk, b)
    bk.new_page()


def alpha_key(b):
    """Sort key for the indexes: ignore a leading article.

    Thirty-one creatures here are called "The Something". Filing them all
    under T means nobody looking for the Bog Hag ever finds her.
    """
    low = b['name'].lower()
    return low[4:] if low.startswith('the ') else low


def page_no(bk, b):
    """The page this creature is on, right-aligned in the margin.

    An index without page numbers makes the reader hunt, which is the one
    thing an index exists to prevent.
    """
    pg = bk.toc.get('mon_%s' % b['slug'])
    if not pg:
        return
    bk.c.setFont(L.LABEL_F, 9)
    bk.c.setFillColor(L.CRIMSON)
    bk.c.drawRightString(PW - M, bk.y, str(pg))


def appendix_az(bk, blocks):
    bk.mark('app_az')
    bk.heading('Monsters by name', 22)
    bk.body(T.APPENDIX_AZ, 10, 13.4)
    bk.y -= 6

    colw = (CW - 20) / 2
    rows = sorted(blocks, key=alpha_key)
    col_top = bk.y               # where a column starts on this page
    col, y = 0, bk.y
    for b in rows:
        if y - 12 < BOT:         # this column is full
            col += 1
            if col > 1:          # both columns full: carry on overleaf
                bk.y = BOT
                bk.new_page()
                col, col_top = 0, TOP
            y = col_top
        x = M + col * (colw + 20)
        y -= 11.6
        bk.c.setFont(L.BODY_F, 9)
        bk.c.setFillColor(L.INK)
        bk.c.drawString(x, y, (b['name'] + (' (boss)' if b['boss'] else ''))[:34])
        bk.c.setFont(L.LABEL_F, 8)
        bk.c.setFillColor(L.MUTED)
        bk.c.drawRightString(x + colw - 24, y, 'CR %s' % b['cr_name'])
        pg = bk.toc.get('mon_%s' % b['slug'])
        if pg:
            bk.c.setFont(L.LABEL_F, 8.5)
            bk.c.setFillColor(L.CRIMSON)
            bk.c.drawRightString(x + colw, y, str(pg))
    bk.y = BOT
    bk.new_page()


def two_col_index(bk, key, title, blurb, groups):
    """A grouped two-column list: heading, then name / CR / page per row.

    `groups` is a list of (group title, [creatures]).
    """
    bk.mark(key)
    bk.heading(title, 22)
    bk.body(blurb, 10, 13.4)
    bk.y -= 6
    colw = (CW - 20) / 2
    col_top, col, y = bk.y, 0, bk.y

    def nextline(h):
        nonlocal col, y, col_top
        if y - h < BOT:
            col += 1
            if col > 1:
                bk.y = BOT
                bk.new_page()
                col, col_top = 0, TOP
            y = col_top
        y -= h
        return M + col * (colw + 20)

    for gtitle, rows in groups:
        if not rows:
            continue
        x = nextline(20)
        bk.c.setFont(L.TITLE_F, 12)
        bk.c.setFillColor(L.CRIMSON)
        bk.c.drawString(x, y, gtitle)
        for b in sorted(rows, key=alpha_key):
            x = nextline(11.6)
            bk.c.setFont(L.BODY_F, 9)
            bk.c.setFillColor(L.INK)
            bk.c.drawString(x + 8, y, b['name'][:30])
            bk.c.setFont(L.LABEL_F, 8)
            bk.c.setFillColor(L.MUTED)
            bk.c.drawRightString(x + colw - 24, y, 'CR %s' % b['cr_name'])
            pg = bk.toc.get('mon_%s' % b['slug'])
            if pg:
                bk.c.setFont(L.LABEL_F, 8.5)
                bk.c.setFillColor(L.CRIMSON)
                bk.c.drawRightString(x + colw, y, str(pg))
    bk.y = BOT
    bk.new_page()


def appendix_type(bk, blocks):
    """By creature kind. What a cleric turns, what a ranger hunts."""
    # Named, not pluralised by adding an s: that gave "Monstrositys",
    # "Undeads" and "Feys" in the first print.
    order = [('aberration', 'Aberrations'), ('beast', 'Beasts'),
             ('celestial', 'Celestials'), ('construct', 'Constructs'),
             ('dragon', 'Dragons'), ('elemental', 'Elementals'),
             ('fey', 'Fey'), ('fiend', 'Fiends'), ('giant', 'Giants'),
             ('humanoid', 'Humanoids'), ('monstrosity', 'Monstrosities'),
             ('ooze', 'Oozes'), ('plant', 'Plants'), ('undead', 'Undead')]
    groups = [(label, [b for b in blocks if b['type'] == t])
              for t, label in order]
    two_col_index(bk, 'app_type', 'Monsters by kind', T.APPENDIX_TYPE, groups)


# Each world of the game, named as the terrain a DM running their own
# campaign would actually look under.
TERRAIN = [
    ('Underground and urban', ['w1', 'w6']),
    ('Arctic', ['w2']),
    ('Desert', ['w3']),
    ('Coast and underwater', ['w4']),
    ('Swamp and marsh', ['w5']),
    ('Ruins and haunted places', ['w7']),
    ('Forest', ['w8']),
    ('Mountain and sky', ['w9']),
    ('The lower planes', ['w10']),
]


def appendix_terrain(bk, blocks):
    groups = [(name, [b for b in blocks if b['world_id'] in ids])
              for name, ids in TERRAIN]
    two_col_index(bk, 'app_terrain', 'Monsters by terrain', T.APPENDIX_TERRAIN,
                  groups)


def appendix_encounters(bk, worlds, blocks):
    """Forty ready-made fights, one for each area, plus the XP arithmetic.

    The book already sorts its creatures into forty areas and tells you what
    party level each was written for. That is an encounter table that was
    never written down.
    """
    bk.chapter = 'Appendix'
    bk.mark('app_enc')
    bk.heading('Encounters', 22)
    bk.body(T.ENCOUNTERS, 10, 13.4)
    bk.y -= 4

    # the threshold table
    bk.space(30)
    bk.y -= 16
    bk.c.setFont(L.TITLE_F, 13)
    bk.c.setFillColor(L.CRIMSON)
    bk.c.drawString(M, bk.y, 'What a party can take')
    bk.y -= 6
    cols = [0.0, 0.34, 0.51, 0.68, 0.85]
    bk.space(16)
    bk.y -= 12
    bk.c.setFont(L.LABEL_F, 8)
    bk.c.setFillColor(L.MUTED)
    bk.c.drawString(M, bk.y, 'PARTY LEVEL')
    for lbl, f in zip(('EASY', 'MEDIUM', 'HARD', 'DEADLY'), cols[1:]):
        bk.c.drawRightString(M + CW * f + CW * 0.12, bk.y, lbl)
    for lv in range(1, 21):
        lo, med, hard, dead = ENG.THRESHOLDS[lv]
        bk.space(12)
        bk.y -= 11
        bk.c.setFont(L.BODY_F, 9)
        bk.c.setFillColor(L.INK)
        bk.c.drawString(M, bk.y, 'Level %d' % lv)
        bk.c.setFont(L.LABEL_F, 8.5)
        bk.c.setFillColor(L.MUTED)
        for v, f in zip((lo, med, hard, dead), cols[1:]):
            bk.c.drawRightString(M + CW * f + CW * 0.12, bk.y,
                                 '{:,}'.format(v * 4))
    bk.y -= 4
    bk.body(T.ENCOUNTERS_NOTE, 9.5, 12.8)
    bk.new_page()

    # the forty areas
    bk.heading('Forty fights, ready to run', 20)
    bk.body(T.ENCOUNTERS_AREAS, 10, 13.4)
    bk.y -= 4
    for w in worlds:
        # Room for the world's name AND its first area, so a heading never
        # ends up alone at the foot of a page.
        bk.space(34 + 14 + 2 * 12 + 10)
        bk.y -= 18
        bk.c.setFont(L.TITLE_F, 14)
        bk.c.setFillColor(L.CRIMSON)
        bk.c.drawString(M, bk.y, w['name'])
        bk.y -= 4
        for a_i in range(4):
            inarea = [b for b in blocks
                      if b['world_i'] == w['i'] and b['area_i'] == a_i]
            if not inarea:
                continue
            mobs = [b for b in inarea if not b['boss']]
            bosses = [b for b in inarea if b['boss']]
            pl = inarea[0]['party_level']
            # The area's heading and both of its encounters stay together.
            # Split across a page they leave an orphan "Boss fight." line
            # under no heading at all.
            bk.space(14 + 2 * 12 + 10)
            bk.y -= 14
            bk.c.setFont(L.BODY_B, 10)
            bk.c.setFillColor(L.INK)
            bk.c.drawString(M, bk.y, w['areas'][a_i]['name'])
            bk.c.setFont(L.LABEL_F, 8)
            bk.c.setFillColor(L.MUTED)
            bk.c.drawRightString(PW - M, bk.y, 'LEVEL %d PARTY OF FOUR' % pl)
            for label, group, adj, word in ENG.suggest_encounters(
                    mobs, bosses[-1] if bosses else None, pl):
                counts = {}
                for b in group:
                    counts[b['name']] = counts.get(b['name'], 0) + 1
                txt = ', '.join('%d %s' % (n, nm) if n > 1 else nm
                                for nm, n in counts.items())
                bk.space(14)
                bk.y -= 12
                runs = [('%s. ' % label, L.BODY_BI), (txt, L.BODY_F),
                        ('  —  %s, %s XP' % (word, '{:,}'.format(adj)),
                         L.BODY_I)]
                L.draw_rich(bk.c, runs, M + 10, bk.y + 9, 9, CW - 10, 11.6)
    bk.new_page()


def appendix_glance(bk, blocks):
    """Everything on as few pages as possible: CR, AC, HP, page.

    This is the one a DM photocopies and tapes inside the screen.
    """
    bk.mark('app_glance')
    bk.heading('All 168 at a glance', 22)
    bk.body(T.APPENDIX_GLANCE, 10, 13.4)
    bk.y -= 6
    colw = (CW - 18) / 2
    rows = sorted(blocks, key=alpha_key)
    col_top, col, y = bk.y, 0, bk.y
    heads_drawn = set()

    def head(x, yy):
        bk.c.setFont(L.LABEL_F, 7.5)
        bk.c.setFillColor(L.MUTED)
        for lbl, off in (('CR', 0.60), ('AC', 0.73), ('HP', 0.86), ('PG', 1.0)):
            bk.c.drawRightString(x + colw * off, yy, lbl)

    y -= 10
    head(M, y)
    heads_drawn.add((0, bk.page))
    for b in rows:
        if y - 10.4 < BOT:
            col += 1
            if col > 1:
                bk.y = BOT
                bk.new_page()
                col, col_top = 0, TOP
            y = col_top - 10
            head(M + col * (colw + 18), y)
        x = M + col * (colw + 18)
        y -= 10.4
        bk.c.setFont(L.BODY_F, 8.5)
        bk.c.setFillColor(L.CRIMSON if b['boss'] else L.INK)
        bk.c.drawString(x, y, b['name'][:26])
        bk.c.setFont(L.LABEL_F, 8)
        bk.c.setFillColor(L.MUTED)
        bk.c.drawRightString(x + colw * 0.60, y, b['cr_name'])
        bk.c.drawRightString(x + colw * 0.73, y, str(b['ac']))
        bk.c.drawRightString(x + colw * 0.86, y, str(b['hp']))
        pg = bk.toc.get('mon_%s' % b['slug'])
        bk.c.setFillColor(L.CRIMSON)
        bk.c.drawRightString(x + colw, y, str(pg) if pg else '')
    bk.y = BOT


def closing(bk):
    """The last page. A book should not end on a blank leaf."""
    bk.new_page(dark=True)
    bk.chapter = ''
    icon = bk.icon
    iw, ih = brand.fit(icon, 120)
    y = PH - 300
    bk.c.drawImage(icon['path'], (PW - iw) / 2, y, iw, ih, mask='auto')

    y -= 54
    bk.c.setFont(L.TITLE_F, 30)
    bk.c.setFillColor(L.GOLD)
    bk.c.drawCentredString(PW / 2, y, 'That is all of them.')

    y -= 16
    bk.c.setStrokeColor(L.CRIMSON)
    bk.c.setLineWidth(2)
    bk.c.line(PW / 2 - 90, y, PW / 2 + 90, y)

    y -= 34
    for line in (
            'One hundred and sixty-eight monsters, ten worlds, and every one',
            'of them already waiting in the card game they came out of.'):
        bk.c.setFont(L.BODY_F, 12)
        bk.c.setFillColor(L.PARCH)
        bk.c.drawCentredString(PW / 2, y, line)
        y -= 18

    y -= 26
    bk.c.setFont(L.TITLE_F, 20)
    bk.c.setFillColor(L.BRIGHT)
    bk.c.drawCentredString(PW / 2, y, 'Play it free at ' + T.SITE)

    y -= 54
    bk.c.setFont(L.LABEL_F, 9)
    bk.c.setFillColor(L.MUTED)
    bk.c.drawCentredString(PW / 2, y, 'CONTAINS AI-GENERATED CONTENT')

    y -= 30
    for line in L.wrap(T.SRD_SHORT, L.BODY_F, 8, CW - 120):
        bk.c.setFont(L.BODY_F, 8)
        bk.c.setFillColor(L.MUTED)
        bk.c.drawCentredString(PW / 2, y, line)
        y -= 11
    bk.y = BOT


def build(path, toc=None, kdp=False):
    data = json.load(open(os.path.join(BUILD, 'blocks.json'), encoding='utf-8'))
    worlds, blocks = data['worlds'], data['blocks']
    bk = Book(path, toc, kdp=kdp)
    if not kdp:
        # A print interior carries no cover: KDP takes the cover as its own
        # wraparound file.
        cover(bk)
    title_page(bk)
    legal(bk)
    contents(bk, worlds)
    intro(bk)
    for w in worlds:
        world_opener(bk, w, blocks)
        # The rank and file of all four areas run on without a break, then
        # the world's four bosses take a page each at the end.
        #
        # Every area holds three ordinary creatures and two of them fill a
        # page, so when a boss interrupted after each area the third was left
        # alone on a page that was sixty per cent white - forty of them across
        # the book. Letting the areas run together pairs each leftover with
        # the first creature of the next area and the white goes away.
        world_bosses = []
        for a_i in range(4):
            in_area = [b for b in blocks if b['world_i'] == w['i'] and b['area_i'] == a_i]
            mobs = [b for b in in_area if not b['boss']]
            world_bosses += [b for b in in_area if b['boss']]
            bk.space(34)
            bk.y -= 20
            bk.c.setFont(L.TITLE_F, 17)
            bk.c.setFillColor(L.CRIMSON)
            bk.c.drawString(M, bk.y, w['areas'][a_i]['name'])
            bk.c.setFont(L.BODY_I, 9.5)
            bk.c.setFillColor(L.MUTED)
            bk.c.drawRightString(PW - M, bk.y, w['areas'][a_i]['place'])
            bk.y -= 6
            bk.c.setStrokeColor(L.CRIMSON)
            bk.c.setLineWidth(1.6)
            bk.c.line(M, bk.y, PW - M, bk.y)
            bk.y -= 12
            for b in mobs:
                mob_entry(bk, b)
        for b in world_bosses:
            boss_entry(bk, b)
    appendix_encounters(bk, worlds, blocks)
    appendix_cr(bk, blocks)
    appendix_type(bk, blocks)
    appendix_terrain(bk, blocks)
    appendix_az(bk, blocks)
    appendix_glance(bk, blocks)
    closing(bk)
    bk.folio()
    if kdp and bk.page % 2:
        # A printed book has to end on a left-hand page.
        bk.c.showPage()
        bk.page += 1
        bk._origin()
        bk.bg(L.PARCH)
    bk.c.save()
    return bk.marks, bk.page


# KDP's own figures, read off its help pages on 1 November 2026.
SPINE_PER_PAGE = {'standard': 0.002252, 'premium': 0.002347}   # inches
PRINT_COST = {'standard': (1.00, 0.0402), 'premium': (1.00, 0.080)}  # large trim, .com
ROYALTY = 0.60


def kdp_cover(pages, ink='standard'):
    """The wraparound cover: back, spine and front in one PDF.

    Width  = bleed + back + spine + front + bleed
    Height = bleed + trim height + bleed
    """
    spine = pages * SPINE_PER_PAGE[ink] * 72.0
    w = BLEED + PW + spine + PW + BLEED
    h = BLEED + PH + BLEED
    out = os.path.join(DIST, 'Axes-and-Aces-Monster-Manual-KDP-cover.pdf')
    c = canvas.Canvas(out, pagesize=(w, h))
    c.setTitle(T.TITLE + ' - cover')

    word = brand.trimmed(brand.WORD_LOGO, 'wordlogo')
    icon = brand.trimmed(brand.ICON, 'icon')

    c.setFillColor(L.SOOT)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    front_x = BLEED + PW + spine        # left edge of the front cover
    back_x = BLEED

    # ---- front ----
    lw, lh = brand.fit(word, 400)
    ly = h - BLEED - 40 - lh
    c.drawImage(word['path'], front_x + (PW - lw) / 2, ly, lw, lh, mask='auto')
    tb = ly - 34 - 28
    c.setFont(L.TITLE_F, 40)
    c.setFillColor(L.GOLD)
    c.drawCentredString(front_x + PW / 2, tb, 'MONSTER MANUAL')

    img = os.path.join(PANELS, 'demonking_boss.jpg')
    ih = PW * 1088 / 1950
    iy = tb - 30 - ih
    c.drawImage(img, front_x, iy, PW, ih, mask=None)
    for i in range(80):
        c.setFillColorRGB(0.078, 0.063, 0.051, alpha=1.0 - i / 80.0)
        c.rect(front_x, iy + ih - (i + 1) * 78 / 80.0, PW, 78 / 80.0 + 0.6,
               stroke=0, fill=1)
        c.rect(front_x, iy + i * 78 / 80.0, PW, 78 / 80.0 + 0.6, stroke=0, fill=1)
    c.setFillAlpha(1)

    y = iy - 20
    c.setFillColor(L.CRIMSON)
    c.rect(front_x + M, y, PW - 2 * M, 3, stroke=0, fill=1)
    c.setFont(L.TITLE_F, 26)
    c.setFillColor(L.PARCH)
    c.drawCentredString(front_x + PW / 2, y - 33, '168 monsters. Ten worlds.')
    c.setFont(L.BODY_F, 12.5)
    c.drawCentredString(front_x + PW / 2, y - 55,
                        'From the free card game at ' + T.SITE)
    c.setFont(L.LABEL_F, 11.5)
    c.setFillColor(L.GOLD)
    c.drawCentredString(front_x + PW / 2, y - 80, T.TAGLINE.upper())

    # ---- spine (KDP allows spine text above 79 pages) ----
    # KDP wants at least 0.0625 in between spine text and each spine edge,
    # and warns of that much drift again when the book is bound. Sizing the
    # type to 45% of the spine leaves roughly double the minimum.
    clearance = 4.5                                   # 0.0625 in in points
    if spine >= 16:
        fs = min(18.0, spine * 0.45)
        if (spine - fs) / 2 >= clearance:
            c.saveState()
            c.translate(front_x - spine / 2, h / 2)
            c.rotate(-90)
            c.setFont(L.TITLE_F, fs)
            c.setFillColor(L.GOLD)
            c.drawCentredString(0, -fs * 0.34,
                                'AXES & ACES  ·  MONSTER MANUAL')
            c.restoreState()

    # ---- back ----
    bx = back_x + M
    bw = PW - 2 * M
    ty = h - BLEED - 72
    c.setFont(L.TITLE_F, 26)
    c.setFillColor(L.BRIGHT)
    c.drawString(bx, ty, '168 monsters. Ten worlds.')
    ty -= 10
    c.setFillColor(L.CRIMSON)
    c.rect(bx, ty, bw, 2.5, stroke=0, fill=1)
    ty -= 14

    for para in T.BACK_COVER.split('\n\n'):
        for line in L.wrap(para, L.BODY_F, 11.5, bw):
            ty -= 15.5
            c.setFont(L.BODY_F, 11.5)
            c.setFillColor(L.PARCH)
            c.drawString(bx, ty, line)
        ty -= 7

    ty -= 16
    c.setFont(L.LABEL_F, 10)
    c.setFillColor(L.GOLD)
    c.drawString(bx, ty, T.TAGLINE.upper())

    # A row of monsters across the middle, which is what the back of a
    # bestiary is for, and what fills the space the copy leaves.
    show = ['goblin', 'frostgiant', 'kraken', 'lich']
    gap = 10.0
    tw = (bw - gap * (len(show) - 1)) / len(show)
    th = tw * 602 / 1080
    # Sit the strip in the gap between the copy and the footer rather than
    # straight under the copy, so the back reads as balanced.
    ty = BLEED + 215
    for i, slug in enumerate(show):
        src = os.path.join(PANELS, slug + '_mob.jpg')
        if not os.path.exists(src):
            src = os.path.join(PANELS, slug + '_boss.jpg')
            ih2 = tw * 1088 / 1950
        else:
            ih2 = th
        x = bx + i * (tw + gap)
        c.setFillColor(L.SOOT)
        c.rect(x + 2, ty - 2, tw, ih2, stroke=0, fill=1)
        c.drawImage(src, x, ty, tw, ih2, mask=None)
        c.setStrokeColor(L.SOOT)
        c.setLineWidth(1.6)
        c.rect(x, ty, tw, ih2, stroke=1, fill=0)

    ic = 46
    c.drawImage(icon['path'], bx, BLEED + 96, ic, ic, mask='auto')
    c.setFont(L.BODY_F, 10)
    c.setFillColor(L.PARCH)
    c.drawString(bx + ic + 12, BLEED + 120, 'Play the game free at ' + T.SITE)
    c.setFont(L.BODY_F, 8.5)
    c.setFillColor(L.MUTED)
    c.drawString(bx + ic + 12, BLEED + 104, 'Contains AI-generated content.')

    # KDP prints the barcode bottom-right of the back cover: keep it clear.
    c.save()
    return out, w, h, spine


def costs(pages):
    rows = []
    for ink in ('standard', 'premium'):
        fixed, per = PRINT_COST[ink]
        cost = fixed + pages * per
        rows.append((ink, cost, cost / ROYALTY))
    return rows


def main():
    os.makedirs(DIST, exist_ok=True)
    L.register()
    tmp = os.path.join(BUILD, 'pass1.pdf')
    marks, pages = build(tmp)
    out = os.path.join(DIST, 'Axes-and-Aces-Monster-Manual.pdf')
    marks2, pages2 = build(out, marks)
    print('digital edition (itch.io)')
    print('  pages: %d' % pages2)
    print('  size:  %.1f MB' % (os.path.getsize(out) / 1e6))
    print('  out:   %s' % os.path.abspath(out))
    if pages != pages2:
        print('  NOTE: page count moved between passes (%d -> %d); '
              'contents numbers may be off by a page.' % (pages, pages2))

    if '--no-kdp' in sys.argv:
        return
    ktmp = os.path.join(BUILD, 'kdp1.pdf')
    kmarks, kpages = build(ktmp, kdp=True)
    kout = os.path.join(DIST, 'Axes-and-Aces-Monster-Manual-KDP-interior.pdf')
    _, kpages2 = build(kout, kmarks, kdp=True)
    ink = 'premium' if '--premium' in sys.argv else 'standard'
    cov, cw, ch, spine = kdp_cover(kpages2, ink)
    print()
    print('print edition (Amazon KDP paperback, 8.5 x 11 in)')
    print('  interior pages: %d  (even: %s)' % (kpages2, kpages2 % 2 == 0))
    print('  interior size:  %.1f MB  (KDP allows 650 MB)'
          % (os.path.getsize(kout) / 1e6))
    print('  interior sheet: %.3f x %.3f in  (trim 8.5 x 11 plus bleed)'
          % ((PW + BLEED) / 72, (PH + 2 * BLEED) / 72))
    print('  interior:       %s' % os.path.abspath(kout))
    print('  cover sheet:    %.3f x %.3f in, spine %.3f in (%s colour)'
          % (cw / 72, ch / 72, spine / 72, ink))
    other = 'premium' if ink == 'standard' else 'standard'
    print('  NOTE: the spine is sized for %s colour. Switching to %s changes'
          % (ink, other))
    print('        it to %.3f in, so rebuild the cover with'
          % (kpages2 * SPINE_PER_PAGE[other]))
    print('        python src/book.py %s'
          % ('--premium' if other == 'premium' else '(no flag)'))
    print('  cover size:     %.1f MB  (KDP wants under 40 MB)'
          % (os.path.getsize(cov) / 1e6))
    print('  cover:          %s' % os.path.abspath(cov))
    print()
    print()
    print('  printing cost and the lowest list price it allows, Amazon.com:')
    for ink, cost, floor in costs(kpages2):
        print('    %-9s $%5.2f per copy  ->  list at least $%5.2f'
              % (ink, cost, floor))


if __name__ == '__main__':
    main()
