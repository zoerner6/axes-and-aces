"""Composite each monster into its own scene, as a comic panel.

The game's monster art is cut out with a transparent background at 420 pixels
tall, and the scene backgrounds are 1280x714. Putting the two together is both
what the brand asks for (a creature inside a real scene, never on a blank
field) and the only way to get a panel big enough to print, since the scene
carries the resolution.

The monster layer is enlarged, never past MAX_UP, so it stays honest.
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

W1_BG = ['tavern', 'cellar', 'forest', 'castle']


def bg_name(world_id, area_i):
    return 'bg_%s.webp' % W1_BG[area_i] if world_id == 'w1' \
        else 'bg_%s_%d.webp' % (world_id, area_i)


def panel(slug, world_id, area_i, size, out_path):
    bg = Image.open(os.path.join(ART, bg_name(world_id, area_i))).convert('RGB')
    bg = bg.resize(size, Image.LANCZOS)

    mon = Image.open(os.path.join(ART, slug + '.webp')).convert('RGBA')
    # Trim the transparent border so the creature itself fills the frame.
    box = mon.getbbox()
    if box:
        mon = mon.crop(box)
    want_h = int(size[1] * 0.74)
    scale = min(want_h / mon.height, MAX_UP)
    new = (max(1, int(mon.width * scale)), max(1, int(mon.height * scale)))
    mon = mon.resize(new, Image.LANCZOS)

    # A soft shadow under it so it sits in the scene instead of on top of it.
    shadow = Image.new('RGBA', size, (0, 0, 0, 0))
    blob = Image.new('RGBA', (int(mon.width * 0.85), int(mon.height * 0.13)),
                     (0, 0, 0, 150))
    sx = (size[0] - blob.width) // 2
    sy = size[1] - int(size[1] * 0.10) - blob.height // 2
    shadow.paste(blob, (sx, sy))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size[1] // 42))
    out = Image.alpha_composite(bg.convert('RGBA'), shadow)

    mx = (size[0] - mon.width) // 2
    my = size[1] - int(size[1] * 0.08) - mon.height
    out.alpha_composite(mon, (mx, max(0, my)))
    out.convert('RGB').save(out_path, 'JPEG', quality=92,
                            subsampling=0, optimize=True)
    return scale


def main():
    os.makedirs(OUT, exist_ok=True)
    data = json.load(open(os.path.join(HERE, '..', 'build', 'blocks.json'),
                          encoding='utf-8'))
    worst, made = 0, 0
    for b in data['blocks']:
        size = BOSS if b['boss'] else MOB
        dest = os.path.join(OUT, '%s_%s.jpg' % (b['slug'], 'boss' if b['boss'] else 'mob'))
        if not os.path.exists(dest) or '--force' in sys.argv:
            s = panel(b['slug'], b['world_id'], b['area_i'], size, dest)
            worst = max(worst, s)
            made += 1
    print('panels written: %d (of %d)' % (made, len(data['blocks'])))
    print('largest creature enlargement used: %.2fx (cap %.1fx)' % (worst, MAX_UP))
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('panel folder: %.1f MB' % (total / 1e6))


if __name__ == '__main__':
    main()
