"""Merge the creature tables, build every stat block, and check the result."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import creatures, creatures2, creatures3          # noqa: E402
from engine import build, cr_name                 # noqa: E402

BUILD = os.path.join(HERE, '..', 'build')

KINDS = {}
for mod in (creatures, creatures2, creatures3):
    for slug, kind in mod.KINDS.items():
        assert slug not in KINDS, 'duplicate creature entry: ' + slug
        KINDS[slug] = kind

data = json.load(open(os.path.join(BUILD, 'roster.json'), encoding='utf-8'))
roster, worlds = data['roster'], data['worlds']

missing = sorted({m['slug'] for m in roster} - set(KINDS))
extra = sorted(set(KINDS) - {m['slug'] for m in roster})
if missing or extra:
    print('MISSING from creature tables (%d): %s' % (len(missing), missing))
    print('EXTRA, not in the game (%d): %s' % (len(extra), extra))
    sys.exit(1)

blocks = [build(m, KINDS[m['slug']]) for m in roster]

# ---- sanity checks ----
problems = []
for b in blocks:
    if b['hp'] < 1:
        problems.append('%s: hp %d' % (b['name'], b['hp']))
    if not 8 <= b['ac'] <= 25:
        problems.append('%s: ac %d' % (b['name'], b['ac']))
    if b['attack']['n'] < 1:
        problems.append('%s: no damage dice' % b['name'])
    for k, v in b['scores'].items():
        if not 1 <= v <= 30:
            problems.append('%s: %s %d' % (b['name'], k, v))
    if b['cr'] == 0 and b['boss']:
        problems.append('%s: boss at CR 0' % b['name'])
if problems:
    print('PROBLEMS:')
    for p in problems[:40]:
        print('  ' + p)
    sys.exit(1)

json.dump({'worlds': worlds, 'blocks': blocks},
          open(os.path.join(BUILD, 'blocks.json'), 'w', encoding='utf-8'), indent=1)

print('built %d stat blocks, no problems' % len(blocks))
print()
print('%-22s %-5s %-5s %4s %4s  %s' % ('', 'party', 'CR', 'AC', 'HP', 'kind'))
for w in worlds:
    bs = [b for b in blocks if b['world_i'] == w['i']]
    pls = sorted({b['party_level'] for b in bs})
    crs = sorted({b['cr'] for b in bs})
    print('%-30s party %s   CR %s..%s' % (
        w['name'], '-'.join(str(p) for p in (pls[0], pls[-1])),
        cr_name(crs[0]), cr_name(crs[-1])))

print()
print('--- a look at four of them ---')
for slug in ('goblin', 'dragon', 'lich', 'demonking'):
    b = next(x for x in blocks if x['slug'] == slug)
    a = b['attack']
    print('%-18s CR %-4s party %-3d AC %-3d HP %-4d  %s %s, %dd%d+%d %s  x%d%s' % (
        b['name'], b['cr_name'], b['party_level'], b['ac'], b['hp'],
        a['name'], ('+%d' % a['bonus']), a['n'], a['die'], a['mod'], a['dmg_type'],
        b['swings'], '  heavy' if b['heavy'] else ''))
    print('   %s %s%s | %s' % (b['size'], b['type'],
                               (' ' + b['tag']) if b['tag'] else '', b['align']))
    print('   traits: %s' % ', '.join(b['traits']))
