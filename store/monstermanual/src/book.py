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


class Book:
    def __init__(self, path, toc=None):
        self.c = canvas.Canvas(path, pagesize=letter)
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

    # ---- page plumbing -------------------------------------------------
    def mark(self, key):
        self.marks.setdefault(key, self.page)

    def folio(self, dark=False):
        if self.page == 1:
            return
        self.c.setFont(L.LABEL_F, 8)
        self.c.setFillColor(L.GOLD if dark else L.MUTED)
        self.c.drawCentredString(PW / 2, M - 8, str(self.page))
        if self.chapter and not dark:
            self.c.setFont(L.BODY_I, 7.5)
            self.c.setFillColor(L.MUTED)
            self.c.drawRightString(PW - M, PH - M + 10, self.chapter)

    def bg(self, color=L.PARCH):
        self.c.setFillColor(color)
        self.c.rect(0, 0, PW, PH, stroke=0, fill=1)

    def new_page(self, dark=False):
        self.folio(dark)
        self.c.showPage()
        self.page += 1
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
def fade_edge(c, y_edge, depth, up):
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
        c.rect(0, y, PW, step + 0.6, stroke=0, fill=1)
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
    c.drawImage(img, 0, iy, PW, ih, mask=None)
    fade_edge(c, iy + ih, 78, up=False)        # top edge of the art
    fade_edge(c, iy, 78, up=True)              # bottom edge

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
    rows += [('Monsters by challenge rating', 'app_cr'),
             ('Monsters by name', 'app_az')]
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
    c.drawImage(img, 0, PH - ih, PW, ih, mask=None)
    fade_edge(c, PH - ih, 80, up=True)         # bottom edge of the art

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
    top = bk.y
    bk.panel_img(b['slug'], False, M, top, PANEL_W)
    ly = provenance(bk, b, M, top - PANEL_H - 6, PANEL_W)
    flavor(bk, b, M, ly, PANEL_W)
    SB.draw(bk.c, parts, b, M + PANEL_W + GUTTER, top, BLOCK_W)
    bk.y = top - need + 4
    bk.c.setStrokeColor(L.PARCH_D)
    bk.c.setLineWidth(1)
    bk.c.line(M, bk.y + 2, PW - M, bk.y + 2)


def boss_entry(bk, b):
    if bk.y < TOP - 2:
        bk.new_page()
    c = bk.c
    top = bk.y
    ph = bk.panel_img(b['slug'], True, M, top, CW)
    y = top - ph - 12

    c.setFont(L.LABEL_F, 9)
    c.setFillColor(L.CRIMSON)
    c.drawString(M, y, 'BOSS · %s · FOR A LEVEL %d PARTY'
                 % (b['area'].upper(), b['party_level']))
    y -= 8
    y = flavor(bk, b, M, y, CW)
    y -= 8

    parts = SB.parts_for(b)
    colw = (CW - 22) / 2
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
        rows = sorted((b for b in blocks if b['cr'] == cr), key=lambda b: b['name'])
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
            bk.c.drawRightString(PW - M, bk.y, '%s · %s' % (b['world'], b['size']))
    bk.new_page()


def appendix_az(bk, blocks):
    bk.mark('app_az')
    bk.heading('Monsters by name', 22)
    bk.body(T.APPENDIX_AZ, 10, 13.4)
    bk.y -= 6

    colw = (CW - 20) / 2
    rows = sorted(blocks, key=lambda b: b['name'].lower())
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
        bk.c.drawString(x, y, (b['name'] + (' (boss)' if b['boss'] else ''))[:40])
        bk.c.setFont(L.LABEL_F, 8)
        bk.c.setFillColor(L.MUTED)
        bk.c.drawRightString(x + colw, y, 'CR %s' % b['cr_name'])
    bk.y = BOT


def build(path, toc=None):
    data = json.load(open(os.path.join(BUILD, 'blocks.json'), encoding='utf-8'))
    worlds, blocks = data['worlds'], data['blocks']
    bk = Book(path, toc)
    cover(bk)
    title_page(bk)
    legal(bk)
    contents(bk, worlds)
    intro(bk)
    for w in worlds:
        world_opener(bk, w, blocks)
        for a_i in range(4):
            in_area = [b for b in blocks if b['world_i'] == w['i'] and b['area_i'] == a_i]
            mobs = [b for b in in_area if not b['boss']]
            bosses = [b for b in in_area if b['boss']]
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
            for b in bosses:
                boss_entry(bk, b)
    appendix_cr(bk, blocks)
    appendix_az(bk, blocks)
    bk.folio()
    bk.c.save()
    return bk.marks, bk.page


def main():
    os.makedirs(DIST, exist_ok=True)
    L.register()
    tmp = os.path.join(BUILD, 'pass1.pdf')
    marks, pages = build(tmp)
    out = os.path.join(DIST, 'Axes-and-Aces-Monster-Manual.pdf')
    marks2, pages2 = build(out, marks)
    print('pages: %d' % pages2)
    print('size:  %.1f MB' % (os.path.getsize(out) / 1e6))
    print('out:   %s' % os.path.abspath(out))
    if pages != pages2:
        print('NOTE: page count moved between passes (%d -> %d); '
              'contents numbers may be off by a page.' % (pages, pages2))


if __name__ == '__main__':
    main()
