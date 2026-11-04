"""Composite each monster into its own scene, as a comic panel.

The game's monster art is cut out with a transparent background at 420 pixels
tall, and the scene backgrounds are 1280x714. Putting the two together is both
what the brand asks for (a creature inside a real scene, never on a blank
field) and the only way to get a panel big enough to print, since the scene
carries the resolution.

The monster layer is enlarged, never past MAX_UP, so it stays honest.

Cut-off art
-----------
Much of the art was drawn to the edge of its own canvas, so the cutout ends
in a dead straight line: the Bog Hag loses 280 pixels across her bottom, the
Ice Witch 253, the Lich 248. Dropped into a scene that line reads as a
printing fault, not as art. Two things are done about it:

  * The worst cut edge is run off the side of the panel, where the panel's
    own black border covers it, so the creature reads as continuing past the
    frame. That is ordinary comic grammar.
  * Any cut edge that cannot be run off, because the opposite edge is cut
    too, is feathered instead, so the silhouette dissolves into the scene
    rather than stopping at a razor line.

A creature bleeding off the bottom gets no ground shadow, because a shadow
under a body that continues past the frame is wrong.
"""
import json, os, sys
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ART = os.path.join(ROOT, 'art')
OUT = os.path.join(HERE, '..', 'build', 'panels')

MOB = (1080, 602)        # 3.6 x 2.01 in at 300 dpi
BOSS = (1950, 1088)      # 6.5 x 3.63 in at 300 dpi
MAX_UP = 1.8             # never enlarge the creature past this

ALPHA_ON = 24            # alpha above this counts as paint
CUT_FRAC = 0.10          # a cut this much of an edge is worth handling
FEATHER = 0.045          # feathered band, as a fraction of the shorter side

W1_BG = ['tavern', 'cellar', 'forest', 'castle']


def bg_name(world_id, area_i):
    return 'bg_%s.webp' % W1_BG[area_i] if world_id == 'w1' \
        else 'bg_%s_%d.webp' % (world_id, area_i)


def cut_edges(im):
    """How much of each edge of the cutout is solid paint, 0 to 1.

    A high number means the drawing was clipped by its own canvas on that
    side, so the silhouette ends in a straight line there.
    """
    a = im.split()[-1]
    w, h = im.size
    px = a.load()
    top = sum(1 for x in range(w) if px[x, 0] > ALPHA_ON) / float(w)
    bottom = sum(1 for x in range(w) if px[x, h - 1] > ALPHA_ON) / float(w)
    left = sum(1 for y in range(h) if px[0, y] > ALPHA_ON) / float(h)
    right = sum(1 for y in range(h) if px[w - 1, y] > ALPHA_ON) / float(h)
    return {'top': top, 'bottom': bottom, 'left': left, 'right': right}


def feather(im, sides, band):
    """Fade the alpha to nothing across `band` pixels on the named sides."""
    if not sides:
        return im
    im = im.copy()
    a = im.split()[-1]
    px = a.load()
    w, h = im.size
    band = max(2, int(band))
    for s in sides:
        for i in range(band):
            k = (i + 1) / float(band + 1)        # 0 at the edge, 1 inward
            if s == 'bottom':
                y = h - 1 - i
                for x in range(w):
                    px[x, y] = int(px[x, y] * k)
            elif s == 'top':
                for x in range(w):
                    px[x, i] = int(px[x, i] * k)
            elif s == 'left':
                for y in range(h):
                    px[i, y] = int(px[i, y] * k)
            elif s == 'right':
                x = w - 1 - i
                for y in range(h):
                    px[x, y] = int(px[x, y] * k)
    im.putalpha(a)
    return im


def place(cuts, size, mon_size):
    """Where to put the creature, and which cut edges need feathering.

    Only a cut bottom is run off the panel. That is the common case and it
    reads correctly, because a creature whose legs leave the frame still
    looks like it is standing in the scene, and the panel's own border
    covers the cut.

    A cut top, left or right is feathered where it is instead. Running one
    of those off the frame drags the creature into a corner and leaves it
    hanging in mid-air: the Demon Sorcerer's cut top is his raised flame,
    not his head, and pinning it to the ceiling lifted his feet off the
    floor. Fading the edge keeps him standing and still kills the hard line.
    """
    pw, ph = size
    mw, mh = mon_size
    bad = [k for k, v in cuts.items() if v >= CUT_FRAC]

    mx = (pw - mw) // 2
    my = ph - int(ph * 0.08) - mh               # the usual inset
    bleed = None

    if 'bottom' in bad:
        bleed, my = 'bottom', ph - mh

    soft = [s for s in ('top', 'left', 'right') if s in bad]
    return mx, my, bleed, soft


def panel(slug, world_id, area_i, size, out_path):
    bg = Image.open(os.path.join(ART, bg_name(world_id, area_i))).convert('RGB')
    bg = bg.resize(size, Image.LANCZOS)

    mon = Image.open(os.path.join(ART, slug + '.webp')).convert('RGBA')
    cuts = cut_edges(mon)
    # Trim the transparent border so the creature itself fills the frame.
    box = mon.getbbox()
    if box:
        mon = mon.crop(box)
    want_h = int(size[1] * 0.74)
    scale = min(want_h / mon.height, MAX_UP)
    new = (max(1, int(mon.width * scale)), max(1, int(mon.height * scale)))
    mon = mon.resize(new, Image.LANCZOS)

    mx, my, bleed, soft = place(cuts, size, mon.size)
    if soft:
        mon = feather(mon, soft, min(mon.size) * FEATHER)

    out = bg.convert('RGBA')
    if bleed != 'bottom':
        # A soft shadow so it sits in the scene instead of on top of it. A
        # creature running off the bottom of the frame does not get one.
        shadow = Image.new('RGBA', size, (0, 0, 0, 0))
        blob = Image.new('RGBA', (int(mon.width * 0.85), int(mon.height * 0.13)),
                         (0, 0, 0, 150))
        sx = (size[0] - blob.width) // 2
        sy = min(size[1] - 1, my + mon.height - blob.height // 2)
        shadow.paste(blob, (sx, max(0, sy)))
        shadow = shadow.filter(ImageFilter.GaussianBlur(size[1] // 42))
        out = Image.alpha_composite(out, shadow)

    out.alpha_composite(mon, (mx, my))
    out.convert('RGB').save(out_path, 'JPEG', quality=92,
                            subsampling=0, optimize=True)
    return scale, bleed, soft


def main():
    os.makedirs(OUT, exist_ok=True)
    data = json.load(open(os.path.join(HERE, '..', 'build', 'blocks.json'),
                          encoding='utf-8'))
    worst, made, bled, softened = 0, 0, [], []
    for b in data['blocks']:
        size = BOSS if b['boss'] else MOB
        dest = os.path.join(OUT, '%s_%s.jpg'
                            % (b['slug'], 'boss' if b['boss'] else 'mob'))
        if not os.path.exists(dest) or '--force' in sys.argv:
            s, bleed, soft = panel(b['slug'], b['world_id'], b['area_i'],
                                   size, dest)
            worst = max(worst, s)
            made += 1
            if bleed:
                bled.append('%s:%s' % (b['slug'], bleed))
            if soft:
                softened.append('%s:%s' % (b['slug'], '+'.join(soft)))
    print('panels written: %d (of %d)' % (made, len(data['blocks'])))
    print('largest creature enlargement used: %.2fx (cap %.1fx)' % (worst, MAX_UP))
    print('run off the frame (%d): %s' % (len(bled), ', '.join(bled) or 'none'))
    print('feathered (%d): %s' % (len(softened), ', '.join(softened) or 'none'))
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('panel folder: %.1f MB' % (total / 1e6))


if __name__ == '__main__':
    main()
