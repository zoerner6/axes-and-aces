"""Pull the monster roster out of dev/game.html. Read-only on the game."""
import re, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, 'dev', 'game.html')
OUT = os.path.join(os.path.dirname(__file__), '..', 'build')
os.makedirs(OUT, exist_ok=True)
src = open(SRC, encoding='utf-8').read()


def block(text, i):
    """The text of the [...] that starts at or after index i."""
    i = text.index('[', i)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == '[':
            depth += 1
        elif text[j] == ']':
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    raise ValueError('unbalanced brackets')


def split_top(bracketed):
    """Each top-level [...] group inside a [...] block."""
    inner, out, depth, start = bracketed[1:-1], [], 0, None
    for k, ch in enumerate(inner):
        if ch == '[':
            if depth == 0:
                start = k
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                out.append(inner[start:k + 1])
    return out


def js_strings(text):
    """Every single-quoted JS string in text, honouring backslash escapes."""
    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] == "'":
            buf, i = [], i + 1
            while i < n and text[i] != "'":
                if text[i] == chr(92) and i + 1 < n:
                    buf.append(text[i + 1])
                    i += 2
                else:
                    buf.append(text[i])
                    i += 1
            out.append(''.join(buf))
        i += 1
    return out


def pat_of(s):
    """pat:[1,'B',1.9] -> [1.0, 'B', 1.9]"""
    return [v.strip().strip("'") if "'" in v else float(v) for v in s[1:-1].split(',')]


MON_RE = re.compile(
    r"name:\s*'([^']+)'[^{}]*?hp:\s*([\d.]+)\s*,\s*atk:\s*([\d.]+)\s*,\s*pat:\s*(\[[^\]]*\])")
BOSS_RE = re.compile(
    r"slug:\s*'([^']+)'\s*,\s*name:\s*'([^']+)'\s*,\s*rule:\s*\{\s*off:\s*(\d)\s*\}\s*,\s*pat:\s*(\[[^\]]*\])")


def monsters_in(text):
    return [{'name': m.group(1), 'hp': float(m.group(2)),
             'atk': float(m.group(3)), 'pat': pat_of(m.group(4))}
            for m in MON_RE.finditer(text)]


# ---- WORLDS: already JSON ----
WORLDS = json.loads(block(src, src.index('const WORLDS =')))

# ---- ART map: display name -> art slug ----
i = src.index('const ART = {')
ART = dict(re.findall(r"'([^']+)'\s*:\s*'([^']+)'",
                      src[i + len('const ART = {'): src.index('};', i)]))

# ---- POOLS: world 1, 4 areas x 5 monsters ----
POOLS = [monsters_in(g) for g in split_top(block(src, src.index('let POOLS =')))]
assert len(POOLS) == 4, 'world 1 pools: got %d' % len(POOLS)
for a in POOLS:
    assert len(a) == 5, 'world 1 area size %d' % len(a)

# ---- world 1 area names, bosses, places ----
W1_AREAS = re.findall(r"\{name:'([^']+)'", block(src, src.index('let AREAS =')))
W1_BOSSES = [{'slug': m.group(1), 'name': m.group(2),
              'off': int(m.group(3)), 'pat': pat_of(m.group(4))}
             for m in BOSS_RE.finditer(block(src, src.index('bosses:[')))]
assert len(W1_AREAS) == 4 and len(W1_BOSSES) == 4, (len(W1_AREAS), len(W1_BOSSES))
W1_PLACES = js_strings(block(src, src.index('let PLACES =')))[:4]
assert len(W1_PLACES) == 4, W1_PLACES

SUITS = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
roster, worlds = [], []


def add(world, w_i, area, a_i, mon, boss):
    slug = mon.get('slug') or ART.get(mon['name'])
    assert slug, 'no art slug for ' + mon['name']
    roster.append({
        'slug': slug, 'name': mon['name'],
        'world': world, 'world_i': w_i, 'world_id': 'w1' if w_i == 0 else 'w%d' % (w_i + 1),
        'area': area, 'area_i': a_i,
        'hp': mon.get('hp', 1.0), 'atk': mon.get('atk', 1.0),
        'pat': mon['pat'], 'boss': boss,
        'off_suit': SUITS[mon['off']] if boss and 'off' in mon else None,
    })


# world 1
worlds.append({'id': 'w1', 'i': 0, 'name': 'The Rescue of Anna', 'quest': 'Bring Anna Home',
               'areas': [{'name': n, 'place': p} for n, p in zip(W1_AREAS, W1_PLACES)]})
for a_i, (area, pool) in enumerate(zip(W1_AREAS, POOLS)):
    for mon in pool:
        add('The Rescue of Anna', 0, area, a_i, mon, False)
    add('The Rescue of Anna', 0, area, a_i, W1_BOSSES[a_i], True)

# worlds 2..10
for w_i, W in enumerate(WORLDS, start=1):
    worlds.append({'id': W['id'], 'i': w_i, 'name': W['name'], 'quest': W['quest'],
                   'intro': W['intro'], 'story': W['story'], 'steps': W['steps'],
                   'areas': [{'name': a['name'], 'place': a['place']} for a in W['areas']]})
    for a_i, area in enumerate(W['areas']):
        for mon in area['pool']:
            add(W['name'], w_i, area['name'], a_i, mon, False)
        b = dict(area['boss'])
        b['off'] = b['rule']['off']
        add(W['name'], w_i, area['name'], a_i, b, True)

# ---- level bands, straight from loadWorld() ----
for m in roster:
    w, a = m['world_i'], m['area_i']
    if w == 0:
        lo, hi = [[1, 3], [3, 5], [5, 7], [7, 9]][a]
        m['boss_lv'] = [3, 5, 7, 10][a]
    else:
        off = w * 8
        lo, hi = [[2, 4], [4, 6], [6, 8], [8, 10]][a]
        lo, hi = lo + off, hi + off
        m['boss_lv'] = [4, 6, 8, 10][a] + off
    m['lv_lo'], m['lv_hi'] = lo, hi
    m['lv'] = m['boss_lv'] if m['boss'] else round((lo + hi) / 2)

art_dir = os.path.join(ROOT, 'art')
missing = sorted({m['slug'] for m in roster
                  if not os.path.exists(os.path.join(art_dir, m['slug'] + '.webp'))})
json.dump({'worlds': worlds, 'roster': roster},
          open(os.path.join(OUT, 'roster.json'), 'w', encoding='utf-8'), indent=1)

by_slug = {}
for m in roster:
    by_slug.setdefault(m['slug'], set()).add(m['name'])
shared = {k: sorted(v) for k, v in by_slug.items() if len(v) > 1}

print('worlds      %d' % len(worlds))
print('entries     %d  (bosses %d)' % (len(roster), sum(1 for m in roster if m['boss'])))
print('art slugs   %d distinct' % len(by_slug))
print('missing art %s' % (missing if missing else 'none'))
print('art shared  %s' % (shared if shared else 'none'))
print('game levels %d..%d' % (min(m['lv'] for m in roster), max(m['lv'] for m in roster)))
