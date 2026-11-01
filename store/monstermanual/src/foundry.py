"""Generate the free Foundry VTT module: all 168 monsters plus their art.

Given away, never sold. Foundry's own package listing does not accept
AI-generated art or text, so this installs from a manifest link rather than
from the in-app package browser.

Actor data follows the dnd5e system schema. It has not been loaded into a
live Foundry instance from here, so treat the first install as a test.
"""
import json, os, re, shutil

from families import TRAITS, GUARDS, HEALS
from engine import mod_str, ability_mod, SUIT_RULE
import statblock as SB
import text as T

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(HERE, '..', 'foundry', 'axes-and-aces-monsters')

MODULE_ID = 'axes-and-aces-monsters'
VERSION = '1.0.0'

SIZE = {'Tiny': 'tiny', 'Small': 'sm', 'Medium': 'med', 'Large': 'lg',
        'Huge': 'huge', 'Gargantuan': 'grg'}
DMG_KEY = {'acid': 'acid', 'bludgeoning': 'bludgeoning', 'cold': 'cold',
           'fire': 'fire', 'force': 'force', 'lightning': 'lightning',
           'necrotic': 'necrotic', 'piercing': 'piercing', 'poison': 'poison',
           'psychic': 'psychic', 'radiant': 'radiant', 'slashing': 'slashing',
           'thunder': 'thunder'}
COND_KEY = {'blinded': 'blinded', 'charmed': 'charmed', 'deafened': 'deafened',
            'exhaustion': 'exhaustion', 'frightened': 'frightened',
            'grappled': 'grappled', 'incapacitated': 'incapacitated',
            'paralyzed': 'paralyzed', 'petrified': 'petrified',
            'poisoned': 'poisoned', 'prone': 'prone', 'restrained': 'restrained',
            'stunned': 'stunned', 'unconscious': 'unconscious'}


def keys(values, table):
    """Split a list of written-out damage or condition words into system keys
    plus whatever could not be matched, which goes in the custom field."""
    hit, custom = [], []
    for v in values:
        k = table.get(v.strip().lower())
        if k:
            hit.append(k)
        else:
            custom.append(v)
    return hit, '; '.join(custom)


def senses_of(b):
    out = {'darkvision': 0, 'blindsight': 0, 'tremorsense': 0, 'truesight': 0,
           'units': 'ft', 'special': ''}
    extra = []
    for s in b['senses']:
        m = re.match(r'(darkvision|blindsight|tremorsense|truesight)\s+(\d+)', s.lower())
        if m:
            out[m.group(1)] = int(m.group(2))
        else:
            extra.append(s)
    out['special'] = '; '.join(extra)
    return out


def html(s):
    return '<p>%s</p>' % s.replace('\n\n', '</p><p>')


def feat(name, text):
    return {'name': name, 'type': 'feat',
            'img': 'icons/svg/aura.svg',
            'system': {'description': {'value': html(text)},
                       'activation': {'type': '', 'cost': None}}}


def weapon(b, a, dc):
    reach = a['reach'] or '5 ft.'
    rng = a['range']
    return {
        'name': a['name'], 'type': 'weapon',
        'img': 'icons/svg/sword.svg',
        'system': {
            'description': {'value': html(
                '%s: %s to hit, %s, one target. Hit: %s %s damage.' % (
                    a['kind'], mod_str(a['bonus']),
                    ('range %s' % rng) if rng else ('reach %s' % reach),
                    SB.dmg(a['n'], a['die'], a['mod']), a['dmg_type']))},
            'actionType': 'rwak' if rng else 'mwak',
            'ability': 'dex' if rng else 'str',
            'attack': {'bonus': str(a['bonus']), 'flat': True},
            'damage': {'parts': [['%dd%d + %d' % (a['n'], a['die'], a['mod']),
                                  a['dmg_type']]]},
            'range': {'value': 5 if not rng else None, 'units': 'ft'},
            'type': {'value': 'natural'},
            'equipped': True, 'proficient': 1,
            'activation': {'type': 'action', 'cost': 1},
        },
    }


def actor(b):
    dc = 8 + b['prof'] + ability_mod(b['scores']['con'])
    sc = b['scores']
    sp = b['speed']

    items = []
    for key in b['traits']:
        tname, ttext = TRAITS[key]
        items.append(feat(tname, SB.fill(ttext, b, dc)))
    if b['suit']:
        dtype, flavor = SUIT_RULE[b['suit']]
        extra = " It also can't be charmed." if b['suit'] == 'Hearts' else ''
        items.append(feat('%s-Proof' % b['suit'],
                          '%s It has resistance to %s damage.%s'
                          % (flavor, dtype, extra)))
    if b['swings'] > 1:
        word = {2: 'two', 3: 'three'}[b['swings']]
        items.append(feat('Multiattack', 'The %s makes %s %s attacks.'
                          % (b['name'].lower(), word, b['attack']['name'].lower())))
    items.append(weapon(b, b['attack'], dc))
    if b['heavy']:
        hname, htext = SB.heavy_text(b, b['heavy'], dc)
        items.append(feat(hname.rstrip('.'), htext))
    guard = GUARDS.get(b['guard_key']) if b['guards'] else None
    if guard:
        items.append(feat('%s (%s)' % (guard[0], guard[1].title()),
                          SB.fill(guard[2], b, dc)))
    heal = HEALS.get(b['heal_key']) if b['heals'] else None
    if heal and heal[0] in ('regen', 'regen_plain'):
        tn, tt = TRAITS[heal[0]]
        items.append(feat(tn, SB.fill(tt, b, dc)))
    elif heal:
        items.append(feat('%s (%s)' % (heal[0], heal[1].title()),
                          SB.fill(heal[2], b, dc)))

    res = list(b['res'])
    if b['suit']:
        res.append(SUIT_RULE[b['suit']][0])
    dr, dr_custom = keys(res, DMG_KEY)
    di, di_custom = keys(b['imm'], DMG_KEY)
    dv, dv_custom = keys(b['vuln'], DMG_KEY)
    ci, ci_custom = keys(b['cond_imm'], COND_KEY)

    bio = ('%s</p><p><em>How it fights.</em> %s</p><p><strong>%s &middot; %s</strong> '
           '&middot; written for a level %d party. From the free card game at %s.'
           % (b['desc'], b['tactics'], b['world'], b['area'],
              b['party_level'], T.SITE))

    return {
        '_id': None,
        'name': b['name'],
        'type': 'npc',
        'img': 'modules/%s/art/%s.webp' % (MODULE_ID, b['slug']),
        'system': {
            'abilities': {k: {'value': sc[k], 'proficient': 0} for k in
                          ('str', 'dex', 'con', 'int', 'wis', 'cha')},
            'attributes': {
                'ac': {'flat': b['ac'], 'calc': 'flat',
                       'formula': '', 'label': b['ac_note'] or ''},
                'hp': {'value': b['hp'], 'max': b['hp'],
                       'formula': b['hit_dice'], 'temp': 0, 'tempmax': 0},
                'movement': dict({k: sp.get(k, 0) for k in
                                  ('burrow', 'climb', 'fly', 'swim', 'walk')},
                                 units='ft', hover=False),
                'senses': senses_of(b),
                'prof': b['prof'],
                'spellcasting': '',
            },
            'details': {
                'biography': {'value': '<p>%s</p>' % bio, 'public': ''},
                'alignment': b['align'].title(),
                'type': {'value': b['type'], 'subtype': b['tag'] or '',
                         'swarm': '', 'custom': ''},
                'cr': b['cr'],
                'xp': {'value': b['xp']},
                'source': {'book': T.TITLE, 'custom': T.SITE},
            },
            'traits': {
                'size': SIZE[b['size']],
                'di': {'value': di, 'custom': di_custom, 'bypasses': []},
                'dr': {'value': dr, 'custom': dr_custom, 'bypasses': []},
                'dv': {'value': dv, 'custom': dv_custom, 'bypasses': []},
                'ci': {'value': ci, 'custom': ci_custom},
                'languages': {'value': [], 'custom': b['languages']},
            },
            'skills': {},
        },
        'items': items,
        'prototypeToken': {
            'name': b['name'],
            'texture': {'src': 'modules/%s/art/%s.webp' % (MODULE_ID, b['slug'])},
            'width': {'Tiny': 0.5, 'Small': 1, 'Medium': 1, 'Large': 2,
                      'Huge': 3, 'Gargantuan': 4}[b['size']],
            'height': {'Tiny': 0.5, 'Small': 1, 'Medium': 1, 'Large': 2,
                       'Huge': 3, 'Gargantuan': 4}[b['size']],
            'disposition': -1, 'actorLink': False,
            'sight': {'enabled': True, 'range': 0},
        },
        'folder': None,
    }


MANIFEST = {
    'id': MODULE_ID,
    'title': 'Axes & Aces Monsters',
    'description': (
        '168 monsters from the free card game Axes &amp; Aces, as 5E-compatible '
        'NPCs with their artwork. Companion to the Axes &amp; Aces Monster '
        'Manual. Free. <strong>Contains AI-generated art and AI-assisted '
        'text.</strong>'),
    'version': VERSION,
    'compatibility': {'minimum': '11', 'verified': '12'},
    'relationships': {'systems': [{'id': 'dnd5e', 'type': 'system',
                                   'compatibility': {'minimum': '3.0.0'}}]},
    'authors': [{'name': 'Axes & Aces', 'url': 'https://' + T.SITE}],
    'url': 'https://' + T.SITE,
    'esmodules': ['scripts/aa-monsters.js'],
    'packs': [],
    'license': 'LICENSE.txt',
    'readme': 'README.md',
}

SCRIPT = '''/* Axes & Aces Monsters - builds a compendium of the 168 creatures.
 *
 * Foundry pack formats change between major versions, so rather than ship a
 * prebuilt pack this imports from bundled JSON into a world compendium. Run
 * it once; after that the compendium is yours.
 */
const MODULE = "axes-and-aces-monsters";
const PACK_LABEL = "Axes & Aces Monsters";

async function importMonsters() {
  const res = await fetch(`modules/${MODULE}/data/monsters.json`);
  if (!res.ok) return ui.notifications.error("Axes & Aces: monsters.json is missing.");
  const monsters = await res.json();

  let pack = game.packs.find(p => p.metadata.label === PACK_LABEL
                                  && p.metadata.packageType === "world");
  if (!pack) {
    pack = await CompendiumCollection.createCompendium({
      label: PACK_LABEL, type: "Actor", packageType: "world"
    });
  }

  ui.notifications.info(`Axes & Aces: importing ${monsters.length} monsters...`);
  const existing = new Set((await pack.getIndex()).map(e => e.name));
  const batch = monsters.filter(m => !existing.has(m.name));
  for (const m of batch) {
    const data = foundry.utils.deepClone(m);
    delete data._id;
    await Actor.create(data, { pack: pack.collection, keepId: false });
  }
  ui.notifications.info(`Axes & Aces: ${batch.length} monsters imported into "${PACK_LABEL}".`);
}

Hooks.once("init", () => {
  game.settings.registerMenu(MODULE, "import", {
    name: "Import the monsters",
    label: "Import 168 monsters",
    hint: "Builds a world compendium holding every creature from the book.",
    icon: "fas fa-dragon",
    type: class extends FormApplication {
      render() { importMonsters(); return this; }
    },
    restricted: true
  });
});

Hooks.once("ready", () => {
  if (!game.user.isGM) return;
  game.modules.get(MODULE).api = { importMonsters };
  console.log("Axes & Aces Monsters | ready. "
    + "Run game.modules.get('axes-and-aces-monsters').api.importMonsters() "
    + "or use the module settings button.");
});
'''

README = '''# Axes & Aces Monsters

168 monsters from the free card game **Axes & Aces**, as 5E-compatible NPCs
with their artwork, for Foundry VTT. Free, and always will be.

This is the companion to the *Axes & Aces Monster Manual*. The book has the
stat blocks laid out properly, the fiction, and the method behind the
challenge ratings. This module just gets the creatures into your game.

## Contains AI-generated content

Every picture here was generated with an AI image model, and the text was
written with AI assistance. That is stated up front so you can decide before
you install it rather than after.

## Installing

Foundry's package browser does not list modules containing AI-generated art,
so install this from the manifest link instead:

1. In Foundry, go to **Add-on Modules** and click **Install Module**.
2. Paste the manifest URL into the **Manifest URL** box at the bottom.
3. Click **Install**.

Then enable it in your world, open **Module Settings**, and click
**Import 168 monsters**. It builds a world compendium called
"Axes & Aces Monsters". You only need to do that once.

## Requirements

Foundry VTT v11 or later, with the **dnd5e** system v3.0 or later.

## Licence

''' + T.SRD_NOTICE + '''

''' + T.SRD_MODIFICATIONS + '''

The artwork and the creature names are the property of the publisher and are
free to use at your own table. Play the game free at ''' + T.SITE + '''.
'''


def main():
    blocks = json.load(open(os.path.join(HERE, '..', 'build', 'blocks.json'),
                            encoding='utf-8'))['blocks']
    art_out = os.path.join(OUT, 'art')
    for d in (OUT, art_out, os.path.join(OUT, 'scripts'), os.path.join(OUT, 'data')):
        os.makedirs(d, exist_ok=True)

    actors = [actor(b) for b in blocks]
    json.dump(actors, open(os.path.join(OUT, 'data', 'monsters.json'), 'w',
                           encoding='utf-8'), indent=1)
    json.dump(MANIFEST, open(os.path.join(OUT, 'module.json'), 'w',
                             encoding='utf-8'), indent=2)
    open(os.path.join(OUT, 'scripts', 'aa-monsters.js'), 'w',
         encoding='utf-8').write(SCRIPT)
    open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8').write(README)
    open(os.path.join(OUT, 'LICENSE.txt'), 'w', encoding='utf-8').write(
        T.SRD_NOTICE + '\n\n' + T.SRD_MODIFICATIONS + '\n')

    copied = 0
    for b in blocks:
        src = os.path.join(ROOT, 'art', b['slug'] + '.webp')
        shutil.copyfile(src, os.path.join(art_out, b['slug'] + '.webp'))
        copied += 1

    size = sum(os.path.getsize(os.path.join(dp, f))
               for dp, _, fs in os.walk(OUT) for f in fs)
    print('module written to %s' % os.path.abspath(OUT))
    print('  actors %d, art files %d, total %.1f MB'
          % (len(actors), copied, size / 1e6))


if __name__ == '__main__':
    main()
