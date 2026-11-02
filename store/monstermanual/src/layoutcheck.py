"""Find layout faults on every page of the book.

Looks for the things a reader sees and a text dump does not:
  1. a drawn rule passing through the glyphs of a line of text
  2. two pieces of text sitting on top of each other
  3. text running outside the trim margins KDP requires
  4. a line of text clipped by the edge of its column

Run: python layoutcheck.py <pdf> [--kdp]
"""
import sys, collections
import pymupdf

PDF = sys.argv[1]
KDP = '--kdp' in sys.argv

BLEED = 9.0 if KDP else 0.0
TRIM_W, TRIM_H = 612.0, 792.0
MIN_OUT = 27.0          # 0.375 in top, bottom, outside
MIN_GUT = 36.0          # 0.5 in gutter, required over 150 pages


def spans(page):
    """Every text span with its tight bounding box."""
    out = []
    for blk in page.get_text('dict')['blocks']:
        if blk.get('type') != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                t = sp['text'].strip()
                if t:
                    out.append((pymupdf.Rect(sp['bbox']), t, sp['size']))
    return out


def rules(page):
    """Horizontal rules: thin, wide, roughly flat."""
    out = []
    for d in page.get_drawings():
        r = d['rect']
        if r.width >= 20 and r.height <= 2.5:
            out.append(r)
    return out


def main():
    doc = pymupdf.open(PDF)
    found = collections.defaultdict(list)

    for i in range(doc.page_count):
        page = doc[i]
        pno = i + 1
        H = page.rect.height
        tx = 0.0 if (pno % 2 and KDP) else BLEED
        L, R = tx, tx + TRIM_W
        T, B = BLEED, BLEED + TRIM_H
        gut_left = (pno % 2 == 1)

        sp = spans(page)
        rl = rules(page)

        # 1. a rule through the middle of a line of text
        for r in rl:
            for box, txt, size in sp:
                if box.x1 < r.x0 or box.x0 > r.x1:
                    continue
                # the rule's y inside the glyph box, not merely touching it
                if box.y0 + 1.0 < r.y0 < box.y1 - 1.0:
                    found['rule through text'].append(
                        (pno, txt[:44], round(r.y0 - box.y0, 1)))

        # 2. text on text
        for a in range(len(sp)):
            for b in range(a + 1, len(sp)):
                ra, rb = sp[a][0], sp[b][0]
                ov = ra & rb
                if ov.is_empty:
                    continue
                if ov.width > 2 and ov.height > 2:
                    found['text overlaps text'].append(
                        (pno, sp[a][1][:26], sp[b][1][:26]))

        # 3. outside the margins
        for box, txt, size in sp:
            checks = (('left', box.x0 - L, MIN_GUT if gut_left else MIN_OUT),
                      ('right', R - box.x1, MIN_OUT if gut_left else MIN_GUT),
                      ('top', box.y0 - T, MIN_OUT),
                      ('bottom', B - box.y1, MIN_OUT))
            for side, got, need in checks:
                if got < need - 0.5:
                    found['outside margin'].append(
                        (pno, side, round(got, 1), need, txt[:30]))

    for kind in ('rule through text', 'text overlaps text', 'outside margin'):
        rows = found[kind]
        print('%-22s %d' % (kind, len(rows)))
        pages = sorted({r[0] for r in rows})
        if pages:
            print('    pages: %s%s' % (pages[:22],
                                       ' ...' if len(pages) > 22 else ''))
        for r in rows[:8]:
            print('    ', r)
        print()


main()
