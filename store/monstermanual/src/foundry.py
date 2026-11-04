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
import legendary as LEG
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


SKILL_KEY = {
    'Acrobatics': 'acr', 'Animal Handling': 'ani', 'Arcana': 'arc',
    'Athletics': 'ath', 'Deception': 'dec', 'History': 'his',
    'Insight': 'ins', 'Intimidation': 'itm', 'Investigation': 'inv',
    'Medicine': 'med', 'Nature': 'nat', 'Perception': 'prc',
    'Performance': 'prf', 'Persuasion': 'per', 'Religion': 'rel',
    'Sleight of Hand': 'slt', 'Stealth': 'ste', 'Survival': 'sur',
}

SAVE_KEY = {'Str': 'str', 'Dex': 'dex', 'Con': 'con', 'Int': 'int',
            'Wis': 'wis', 'Cha': 'cha'}


def save_set(b):
    """Which abilities this creature is proficient in, as system keys.

    The engine writes saves as display strings like "Dex +4", because that
    is what the page prints. Here only the ability matters.
    """
    out = set()
    for s in b.get('saves') or []:
        k = SAVE_KEY.get(s.split()[0])
        if k:
            out.add(k)
    return out


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
    saves = save_set(b)

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
    spells = LEG.SPELLCASTERS.get(b['slug'])
    if spells:
        word, abil, lvl, book = spells
        sm = ability_mod(sc[abil])
        lines = []
        for sl in sorted(book):
            head = ('Cantrips (at will)' if sl == 0 else
                    '%s level (%d slots)' % (LEG.ORDINAL[sl],
                                             LEG.SLOTS[lvl].get(sl, 1)))
            lines.append('<li><strong>%s:</strong> <em>%s</em></li>'
                         % (head, ', '.join(book[sl])))
        items.append(feat('Spellcasting',
                          'The %s is %s. Its spellcasting ability is %s '
                          '(spell save DC %d, %s to hit with spell attacks). '
                          'It has the following spells prepared:<ul>%s</ul>'
                          % (SB.bare(b['name']), word, SB.ABIL_WORD[abil],
                             8 + b['prof'] + sm, mod_str(b['prof'] + sm),
                             ''.join(lines))))

    if b['swings'] > 1:
        word = {2: 'two', 3: 'three'}[b['swings']]
        items.append(feat('Multiattack', 'The %s makes %s %s attacks.'
                          % (SB.bare(b["name"]), word, b["attack"]["name"].lower())))
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

    # Legendary actions. Foundry has no distinct item type for them, so they
    # go in as feats named the way the stat block names them, and the actor
    # gets the three-per-round resource the sheet shows.
    if b['boss']:
        items.append(feat('Legendary Actions',
                          SB.fill(LEG.LEGENDARY_INTRO, b, dc)))
        for lname, cost, ltext in LEG.actions_for(b):
            head = lname if cost == 1 else '%s (Costs %d Actions)' % (lname, cost)
            items.append(feat(head, SB.fill(ltext, b, dc)))

    lair = LEG.lair_for(b)
    if lair:
        place, ldc, effects = lair
        body = ('When fighting inside %s, the %s can take a lair action on '
                'initiative count 20 (losing ties). It cannot do so two rounds '
                'in a row. Choose one:<ul>%s</ul>'
                % (place, SB.bare(b['name']),
                   ''.join('<li>%s</li>' % SB.fill(e, b, dc).replace(
                       '{ld}', str(ldc)) for e in effects)))
        items.append(feat('Lair Actions', body))

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
            'abilities': {k: {'value': sc[k],
                              'proficient': 1 if k in saves else 0}
                          for k in
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
                'spellcasting': (LEG.SPELLCASTERS[b['slug']][1]
                                 if b['slug'] in LEG.SPELLCASTERS else ''),
            },
            'resources': {
                'legact': ({'value': 3, 'max': 3} if b['boss']
                           else {'value': 0, 'max': 0}),
                'legres': ({'value': 3, 'max': 3} if 'legendary' in b['traits']
                           else {'value': 0, 'max': 0}),
                'lair': ({'value': True, 'initiative': 20}
                         if b.get('world_boss') else
                         {'value': False, 'initiative': 0}),
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
            'skills': {SKILL_KEY[n]: {'value': 1} for n in b['skills']
                       if n in SKILL_KEY},
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


# No manifest or download URL on purpose.
#
# Those two fields are what lets anyone with the link install the module,
# and this module ships with the book rather than being given away. Foundry's
# package browser would not have listed it anyway - it refuses packages
# containing AI art - so a public manifest was never a discovery channel,
# only a way for people who had already found the paid page to take the
# monsters without paying. Buyers unzip it into Data/modules by hand, which
# is normal for paid Foundry content.

MANIFEST = {
    'id': MODULE_ID,
    'title': 'Axes & Aces Monsters',
    'description': (
        '168 monsters from the free card game Axes &amp; Aces, as 5E-compatible '
        'NPCs with their artwork. Companion to the Axes &amp; Aces Monster '
        'Manual. Free. <strong>Contains AI-generated art and AI-assisted '
        'text.</strong>'),
    'version': VERSION,
    'compatibility': {'minimum': '11', 'verified': '13'},
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

/* The button lives on the Actors sidebar rather than in a settings menu.
 * A settings menu needs a FormApplication subclass, which Foundry deprecated
 * in v13 and drops in v14; a sidebar button is the same in 11, 12 and 13.
 */
function addButton(html) {
  const root = html instanceof HTMLElement ? html : html[0];
  if (!root || root.querySelector(".aa-import")) return;
  const header = root.querySelector(".header-actions") || root.firstElementChild;
  if (!header) return;
  const b = document.createElement("button");
  b.className = "aa-import";
  b.innerHTML = '<i class="fas fa-dragon"></i> Import Axes &amp; Aces monsters';
  b.addEventListener("click", () => importMonsters());
  header.append(b);
}

Hooks.on("renderActorDirectory", (app, html) => {
  if (game.user?.isGM) addButton(html);
});

Hooks.once("ready", () => {
  if (!game.user.isGM) return;
  game.modules.get(MODULE).api = { importMonsters };
  console.log("Axes & Aces Monsters | ready. "
    + "Use the button on the Actors tab, or run "
    + "game.modules.get('axes-and-aces-monsters').api.importMonsters()");
});
'''

README = '''# Axes & Aces Monsters

168 monsters from the free card game **Axes & Aces**, as 5E-compatible NPCs
with their artwork, for Foundry VTT. Free, and always will be.

This is the companion to the *Axes & Aces Monster Manual*. The book has the
stat blocks laid out properly, the fiction, and the method behind the
challenge ratings. This module just gets the creatures into your game.

## Not yet tested in a live Foundry

Read this before you rely on it. The actor data is built to the dnd5e
schema and every field has been checked, but nobody has installed this
module into a running Foundry and clicked the button. If something is
wrong, that is where it will show. Please say so and it will be fixed:
the issue tracker is on the repository linked above.

## Contains AI-generated content

Every picture here was generated with an AI image model, and the text was
written with AI assistance. That is stated up front so you can decide before
you install it rather than after.

## Installing

This module comes with the *Axes & Aces Monster Manual*, so it installs by
hand rather than from a link:

1. Find your Foundry data folder. In Foundry, **Configuration and Setup →
   Config** shows it; it is usually `FoundryVTT/Data`.
2. Unzip this whole folder into `Data/modules`, so you end up with
   `Data/modules/axes-and-aces-monsters/module.json`.
3. Restart Foundry. The module is now in the **Add-on Modules** list and can
   be enabled in your world.

There is no manifest link. Foundry's package browser does not list modules
containing AI-generated art, and this one is for people who bought the book.

Then enable it in your world, open the **Actors** tab in the sidebar, and
click **Import Axes & Aces monsters** at the top. It builds a world
compendium called "Axes & Aces Monsters". You only need to do that once.

## What each creature carries

Ability scores, armor class, hit points and hit dice, every speed, senses,
languages, challenge rating and XP, damage resistances, immunities and
vulnerabilities, condition immunities, skill proficiencies, saving throw
proficiencies, traits, a weapon attack, and the recharging heavy blow where
the creature has one.

The forty bosses also carry their legendary actions and the three-per-round
resource, the ten that end a world carry their lair actions, and the nine
spellcasters carry their spell lists.

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
