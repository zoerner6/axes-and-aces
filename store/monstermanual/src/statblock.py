"""Build and draw one creature's stat block.

A block is first turned into a list of parts, each of which knows its own
height. That lets the page decide whether the whole entry fits before any of
it is drawn.
"""
from reportlab.pdfbase import pdfmetrics

from families import TRAITS, GUARDS, HEALS
import legendary as LEG
from engine import mod_str, ability_mod, dice_for, SUIT_RULE
from layout import (BODY_F, BODY_I, BODY_B, BODY_BI, LABEL_F, TITLE_F,
                    CRIMSON, INK, MUTED, PARCH_D, wrap, rich_height,
                    draw_rich, draw_para)

SZ = 8.4          # body size inside a block
LEAD = 10.0       # line spacing
GAP = 3.2         # space between parts
ABIL = ['str', 'dex', 'con', 'int', 'wis', 'cha']


def avg_dice(n, die, mod=0):
    return int(n * (die + 1) / 2) + mod


def dmg(n, die, mod=0):
    txt = '%d (%dd%d' % (max(1, avg_dice(n, die, mod)), n, die)
    if mod > 0:
        txt += ' + %d' % mod
    elif mod < 0:
        txt += ' - %d' % abs(mod)
    return txt + ')'


RIDERS = {
    'poison': 'and the target must succeed on a DC {dc} Constitution saving '
              'throw or be poisoned for 1 minute',
    'cold': 'and the target\'s speed is reduced by 10 feet until the end of '
            'its next turn',
    'lightning': 'and the target can\'t take reactions until the start of its '
                 'next turn',
    'thunder': 'and the target must succeed on a DC {dc} Constitution saving '
               'throw or be deafened until the end of its next turn',
    'grapple': 'and the target is grappled (escape DC {dc}) if it is a '
               'creature of the right size. Until this grapple ends, the '
               'target is restrained',
}


def num(n):
    return '{:,}'.format(n)


def parts_for(b):
    """Every part of the block, each with its measured height."""
    P = []

    def add(kind, h, **kw):
        P.append(dict(kind=kind, h=h, **kw))

    name = b['name']
    dc_default = 8 + b['prof'] + ability_mod(b['scores']['con'])

    # --- header ---
    add('name', 17, text=name)
    kind = '%s %s%s, %s' % (b['size'], b['type'],
                            (' (%s)' % b['tag']) if b['tag'] else '',
                            b['align'])
    add('sub', LEAD, text=kind)
    add('rule', GAP + 2)

    # --- defenses ---
    ac = 'Armor Class %d%s' % (b['ac'], (' (%s)' % b['ac_note']) if b['ac_note'] else '')
    add('kv', LEAD, label='Armor Class',
        value='%d%s' % (b['ac'], (' (%s)' % b['ac_note']) if b['ac_note'] else ''))
    add('kv', LEAD, label='Hit Points', value='%d (%s)' % (b['hp'], b['hit_dice']))
    sp = b['speed']
    order = ['walk', 'burrow', 'climb', 'fly', 'swim']
    bits = []
    for k in order:
        if k in sp:
            bits.append(('%d ft.' % sp[k]) if k == 'walk'
                        else '%s %d ft.' % (k, sp[k]))
    add('kv', LEAD, label='Speed', value=', '.join(bits) or '0 ft.')
    add('rule', GAP + 2)

    # --- ability table ---
    add('abils', 24)
    add('rule', GAP + 2)

    # --- the lines that only appear when they have something to say ---
    meta = []
    if b['saves']:
        meta.append(('Saving Throws', ', '.join(b['saves'])))
    if b['skills']:
        meta.append(('Skills', ', '.join(
            '%s %s' % (s, mod_str(b['prof'] + ability_mod(b['scores'][SKILL_ABIL.get(s, 'wis')])))
            for s in b['skills'])))
    if b['vuln']:
        meta.append(('Damage Vulnerabilities', ', '.join(b['vuln'])))
    if b['res']:
        meta.append(('Damage Resistances', ', '.join(b['res'])))
    if b['imm']:
        meta.append(('Damage Immunities', ', '.join(b['imm'])))
    if b['cond_imm']:
        meta.append(('Condition Immunities', ', '.join(b['cond_imm'])))
    senses = list(b['senses'])
    pp = 10 + ability_mod(b['scores']['wis']) + (b['prof'] if 'Perception' in b['skills'] else 0)
    senses.append('passive Perception %d' % pp)
    meta.append(('Senses', ', '.join(senses)))
    meta.append(('Languages', b['languages']))
    meta.append(('Challenge', '%s (%s XP)' % (b['cr_name'], num(b['xp']))))
    for label, value in meta:
        runs = [(label + ' ', BODY_B), (value, BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)
    add('rule', GAP + 2)

    # --- traits ---
    for key in b['traits']:
        tname, ttext = TRAITS[key]
        x = fill(ttext, b, dc_default)
        runs = [(tname + '. ', BODY_BI), (x, BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    # the boss's one trick, carried over from the card game
    if b['suit']:
        dtype, flavor = SUIT_RULE[b['suit']]
        extra = ' It also can\'t be charmed.' if b['suit'] == 'Hearts' else ''
        txt = ('%s It has resistance to %s damage.%s' % (flavor, dtype, extra))
        runs = [('%s-Proof. ' % b['suit'], BODY_BI), (txt, BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    # a turn spent guarding, when it is a trait rather than a reaction
    guard = GUARDS.get(b['guard_key']) if b['guards'] else None
    if guard and guard[1] == 'bonus action':
        gname, _, gtext = guard
        runs = [('%s (Bonus Action). ' % gname, BODY_BI),
                (fill(gtext, b, dc_default), BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    # --- spellcasting ---
    # Nine creatures here are named and described as spellcasters. A lich that
    # cannot cast a spell is not a lich. Every spell is SRD 5.1, and the lists
    # are short on purpose: what it will actually cast, not its whole book.
    spells = LEG.SPELLCASTERS.get(b['slug'])
    if spells:
        word, abil, lvl, book = spells
        sm = ability_mod(b['scores'][abil])
        save_dc = 8 + b['prof'] + sm
        runs = [('Spellcasting. ', BODY_BI),
                ('The %s is %s. Its spellcasting ability is %s (spell save DC %d, '
                 '%s to hit with spell attacks). It has the following spells '
                 'prepared:' % (bare(name), word, ABIL_WORD[abil], save_dc,
                                mod_str(b['prof'] + sm)), BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)
        slots = LEG.SLOTS[lvl]
        for sl in sorted(book):
            if sl == 0:
                head = 'Cantrips (at will): '
            else:
                head = '%s level (%d slots): ' % (LEG.ORDINAL[sl], slots.get(sl, 1))
            runs = [(head, BODY_B), (', '.join(book[sl]), BODY_I)]
            add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs, indent=10)

    # a turn spent healing, when it is regeneration
    heal = HEALS.get(b['heal_key']) if b['heals'] else None
    if heal and heal[0] in ('regen', 'regen_plain'):
        tname, ttext = TRAITS[heal[0]]
        runs = [(tname + '. ', BODY_BI), (fill(ttext, b, dc_default), BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)
        heal = None

    # --- actions ---
    add('head', LEAD + 5, text='Actions')
    if b['swings'] > 1:
        word = {2: 'two', 3: 'three'}[b['swings']]
        txt = 'The %s makes %s %s attacks.' % (bare(name), word,
                                               b['attack']['name'].lower())
        runs = [('Multiattack. ', BODY_BI), (txt, BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    a = b['attack']
    reach = a['reach'] or '5 ft.'
    where = ('range %s' % a['range']) if a['range'] else ('reach %s' % reach)
    line = '%s: %s to hit, %s, one target. Hit: %s %s damage' % (
        a['kind'], mod_str(a['bonus']), where,
        dmg(a['n'], a['die'], a['mod']), a['dmg_type'])
    if a['rider']:
        line += ', ' + RIDERS[a['rider']].replace('{dc}', str(dc_default))
    line += '.'
    runs = [(a['name'] + '. ', BODY_BI), (line, BODY_F)]
    add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    if b['heavy']:
        h = b['heavy']
        hv_name, hv_text = heavy_text(b, h, dc_default)
        runs = [(hv_name + ' ', BODY_BI), (hv_text, BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    if heal and heal[1] == 'action':
        hname, _, htext = heal
        runs = [(hname + '. ', BODY_BI), (fill(htext, b, dc_default), BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)
    elif heal and heal[1] == 'bonus action':
        hname, _, htext = heal
        runs = [('%s (Bonus Action). ' % hname, BODY_BI),
                (fill(htext, b, dc_default), BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    # --- reactions ---
    if guard and guard[1] == 'reaction':
        add('head', LEAD + 5, text='Reactions')
        gname, _, gtext = guard
        runs = [(gname + '. ', BODY_BI), (fill(gtext, b, dc_default), BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)

    # --- legendary actions ---
    # Only bosses, and every boss. One of these fought alone against a party
    # of four otherwise spends the whole fight watching.
    if b['boss']:
        add('head', LEAD + 5, text='Legendary Actions')
        runs = [(fill(LEG.LEGENDARY_INTRO, b, dc_default), BODY_F)]
        add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs)
        for lname, cost, ltext in LEG.actions_for(b):
            head = lname if cost == 1 else '%s (Costs %d Actions)' % (lname, cost)
            runs = [(head + '. ', BODY_BI), (fill(ltext, b, dc_default), BODY_F)]
            add('rich', rich_height(runs, SZ, 0, LEAD), runs=runs, indent=10)

    # --- lair actions ---
    # The creature that ends a world, fought where it lives.
    lair = LEG.lair_for(b)
    if lair:
        place, ldc, effects = lair
        add('head', LEAD + 5, text='Lair Actions')
        intro = ('When fighting inside %s, the %s can take a lair action on '
                 'initiative count 20 (losing ties). It cannot do so two rounds '
                 'in a row. Choose one:' % (place, bare(name)))
        add('rich', rich_height([(intro, BODY_F)], SZ, 0, LEAD),
            runs=[(intro, BODY_F)])
        for e in effects:
            txt = fill(e, b, dc_default).replace('{ld}', str(ldc))
            add('rich', rich_height([(txt, BODY_F)], SZ, 0, LEAD),
                runs=[('• ', BODY_B), (txt, BODY_F)], indent=10)

    return P


def bare(name):
    """The creature's name as it reads inside a sentence.

    Thirty-one creatures here are called "The Something", and every piece of
    SRD trait wording already supplies its own article: "The {n} has
    advantage..." So the article is dropped on the way in, or the page reads
    "The the flame fiend".
    """
    low = name.lower()
    return low[4:] if low.startswith('the ') else low


SKILL_ABIL = {
    'Athletics': 'str', 'Acrobatics': 'dex', 'Sleight of Hand': 'dex',
    'Stealth': 'dex', 'Arcana': 'int', 'History': 'int', 'Investigation': 'int',
    'Nature': 'int', 'Religion': 'int', 'Animal Handling': 'wis',
    'Insight': 'wis', 'Medicine': 'wis', 'Perception': 'wis', 'Survival': 'wis',
    'Deception': 'cha', 'Intimidation': 'cha', 'Performance': 'cha',
    'Persuasion': 'cha',
}


def fill(text, b, dc):
    """Put this creature's name and numbers into a piece of trait wording."""
    hp = b['hp']
    x = {
        'regen': max(2, round(hp * 0.06)),
        'regen_plain': max(2, round(hp * 0.05)),
    }
    small = max(2, round(hp * 0.07))
    aura = max(2, round(b['cr'] * 0.8) if b['cr'] >= 1 else 2)
    # {xd} is the same quantity as {x}, written as dice. Anything that deals
    # damage uses it: every other attack in the book rolls for damage and a
    # bare number next to them reads as a mistake.
    dn, dd = dice_for(small, b['attack']['die'])
    # {xl} is what a legendary action costing three of them is worth: about
    # what the creature's ordinary attack does, which is where the SRD puts it.
    a = b['attack']
    ln, ld = dice_for(avg_dice(a['n'], a['die'], a['mod']), a['die'])
    return (text.replace('{n}', bare(b['name']))
                .replace('{dc}', str(dc))
                .replace('{atk}', mod_str(a['bonus']))
                .replace('{xd}', dmg(dn, dd))
                .replace('{xl}', dmg(ln, ld))
                .replace('{x}', str(small if '{x} hit points' in text or
                                    'regains' in text else
                                    aura if 'fire damage' in text or
                                    'cold damage' in text else small)))


def heavy_text(b, h, dc):
    """The recharging blow, named for what the creature actually does."""
    breath = h.get('breath')
    size = {'Tiny': 15, 'Small': 15, 'Medium': 15, 'Large': 30,
            'Huge': 60, 'Gargantuan': 90}[b['size']]
    total = avg_dice(h['n'], h['die'])
    if breath:
        name = 'Breath Weapon (Recharge 5-6).'
        txt = ('The %s exhales %s in a %d-foot cone. Each creature in that '
               'area must make a DC %d Dexterity saving throw, taking %d '
               '(%dd%d) %s damage on a failed save, or half as much damage on '
               'a successful one.' % (bare(b['name']), BREATH_WORD[breath],
                                      size, dc, total, h['n'], h['die'], breath))
    else:
        name = 'Savage Blow (Recharge 5-6).'
        txt = ('The %s throws everything into one strike. Each creature within '
               '%d feet of it must make a DC %d Dexterity saving throw, taking '
               '%d (%dd%d) %s damage on a failed save, or half as much damage '
               'on a successful one.'
               % (bare(b['name']), max(10, size // 2), dc, total, h['n'],
                  h['die'], b['attack']['dmg_type']))
    return name, txt


ABIL_WORD = {'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
             'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma'}


BREATH_WORD = {
    'fire': 'fire', 'cold': 'an icy blast', 'lightning': 'lightning',
    'necrotic': 'grave air', 'force': 'a storm of splinters', 'poison': 'poison gas',
    'acid': 'acid',
}


def height(parts, width):
    """Total height of the block at this width."""
    total = 0.0
    for p in parts:
        if p['kind'] == 'rich':
            total += rich_height(p['runs'], SZ, width - p.get('indent', 0), LEAD)
        elif p['kind'] == 'kv':
            runs = [(p['label'] + ' ', BODY_B), (p['value'], BODY_F)]
            total += rich_height(runs, SZ, width, LEAD)
        else:
            total += p['h']
    return total


def draw(c, parts, b, x, y, width):
    """Draw the block with its top at y. Returns the bottom y."""
    for p in parts:
        k = p['kind']
        if k == 'name':
            c.setFont(TITLE_F, 15)
            c.setFillColor(CRIMSON)
            c.drawString(x, y - 13, p['text'])
            y -= p['h']
        elif k == 'sub':
            c.setFont(BODY_I, SZ)
            c.setFillColor(MUTED)
            c.drawString(x, y - 8, p['text'])
            y -= p['h']
        elif k == 'head':
            y -= 4
            c.setFont(TITLE_F, 11)
            c.setFillColor(CRIMSON)
            c.drawString(x, y - 9, p['text'])
            y -= LEAD + 1
            c.setStrokeColor(CRIMSON)
            c.setLineWidth(0.6)
            c.line(x, y + 3, x + width, y + 3)
        elif k == 'rule':
            c.setStrokeColor(CRIMSON)
            c.setLineWidth(0.8)
            c.line(x, y - p['h'] / 2, x + width, y - p['h'] / 2)
            y -= p['h']
        elif k == 'kv':
            runs = [(p['label'] + ' ', BODY_B), (p['value'], BODY_F)]
            y = draw_rich(c, runs, x, y, SZ, width, LEAD)
        elif k == 'rich':
            ind = p.get('indent', 0)
            y = draw_rich(c, p['runs'], x + ind, y, SZ, width - ind, LEAD)
        elif k == 'abils':
            y = draw_abils(c, b, x, y, width)
    return y


def draw_abils(c, b, x, y, width):
    col = width / 6.0
    c.setFont(LABEL_F, 8)
    c.setFillColor(CRIMSON)
    for i, a in enumerate(ABIL):
        c.drawCentredString(x + col * (i + 0.5), y - 9, a.upper())
    c.setFont(BODY_F, SZ)
    c.setFillColor(INK)
    for i, a in enumerate(ABIL):
        s = b['scores'][a]
        c.drawCentredString(x + col * (i + 0.5), y - 20,
                            '%d (%s)' % (s, mod_str(ability_mod(s))))
    return y - 24
