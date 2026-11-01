"""Turn Axes & Aces balance numbers into 5e-compatible stat blocks.

The game is tuned for poker hands, not for a party of four, so nothing is
copied across raw. Every number below is derived from the game's own data by
the documented method in the book's introduction:

  1. Where a monster stands in the journey gives the party level it is for.
  2. Its health and attack multipliers give its challenge rating inside that
     band, and its shell-vs-bite balance decides whether that rating is spent
     on armor and hit points or on attack and damage.
  3. Its attack pattern gives it its actions.

Only SRD 5.1 material is used (CC BY 4.0).
"""

CR_LADDER = [0, 0.125, 0.25, 0.5] + list(range(1, 31))

CR_NAME = {0: '0', 0.125: '1/8', 0.25: '1/4', 0.5: '1/2'}

# Experience by challenge rating (SRD 5.1).
CR_XP = {
    0: 10, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450, 3: 700, 4: 1100,
    5: 1800, 6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900, 11: 7200,
    12: 8400, 13: 10000, 14: 11500, 15: 13000, 16: 15000, 17: 18000,
    18: 20000, 19: 22000, 20: 25000, 21: 33000, 22: 41000, 23: 50000,
    24: 62000, 25: 75000, 26: 90000, 27: 105000, 28: 120000, 29: 135000,
    30: 155000,
}

# Hit dice by size (SRD 5.1).
SIZE_DIE = {'Tiny': 4, 'Small': 6, 'Medium': 8, 'Large': 10, 'Huge': 12,
            'Gargantuan': 20}

# A boss's "this suit does no damage" rule, translated for the table.
# In the card game a quarter of your cards bounce off. At a table the nearest
# honest equivalent is resistance to a damage type the party is certainly
# using, so the fight asks them to change their approach the same way.
SUIT_RULE = {
    'Spades': ('slashing', 'Blades turn on it.'),
    'Clubs': ('bludgeoning', 'Blunt force barely marks it.'),
    'Diamonds': ('piercing', 'Points and arrows skate off it.'),
    'Hearts': ('psychic', 'Nothing kind reaches it.'),
}

AREAS_TOTAL = 40  # ten worlds, four areas each


def cr_name(cr):
    return CR_NAME.get(cr, str(int(cr)))


def snap_cr(x):
    """Nearest rung on the challenge rating ladder."""
    return min(CR_LADDER, key=lambda c: (abs(c - x), c))


def party_level(world_i, area_i):
    """Where this area sits in the journey -> the party level it is written for.

    Forty areas spread evenly over levels 1 to 20: two areas per level.
    """
    n = world_i * 4 + area_i
    return max(1, min(20, round(1 + n * 19 / (AREAS_TOTAL - 1))))


def temper(hp, atk):
    """The game's own shell-vs-bite reading. 1 is all armor, 0 is all teeth."""
    return max(0.0, min(1.0, ((hp / atk) - 0.6) / 1.1))


def challenge(mon):
    """Challenge rating for one monster.

    Rank and file come several at a time, so one of them is worth about half
    a party level. A boss is fought alone, so it sits two above.
    """
    pl = party_level(mon['world_i'], mon['area_i'])
    if mon['boss']:
        return snap_cr(pl + 2), pl
    return snap_cr(pl / 2 * (mon['hp'] * mon['atk'])), pl


# ---- what a creature of a given rating is expected to carry ----
# Our own curve, fitted to the SRD's own creatures rather than copied from any
# table: it only has to be smooth, and the same for every monster in the book.

def hp_target(cr):
    if cr <= 0:
        return 4
    if cr < 1:
        return round(8 + (cr - 0.125) * 32)       # 8 at 1/8, 22 at 1/2
    return round(15 * cr + 18)


def ac_target(cr):
    return max(11, min(21, 12 + round(cr / 3)))


def atk_target(cr):
    return max(3, min(16, 4 + round(cr * 0.45)))


def dpr_target(cr):
    """Damage a round, averaged over the fight."""
    if cr < 1:
        return max(2, round(2 + cr * 8))
    return round(6 * cr + 3)


def proficiency(cr):
    return 2 + max(0, (max(1, int(cr + 0.999)) - 1) // 4)


def ability_mod(score):
    return (score - 10) // 2


def dedupe(items):
    """Keep order, drop repeats. Families and creatures often name the same
    trait or resistance twice."""
    seen, out = set(), []
    for v in items:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def mod_str(m):
    return ('+%d' % m) if m >= 0 else str(m)


def avg(die_count, die, bonus):
    return int(die_count * (die + 1) / 2) + bonus


DICE_CHOICES = [(n, d) for d in (4, 6, 8, 10, 12) for n in range(1, 5)]
AREA_CHOICES = [(n, d) for d in (6, 8, 10, 12) for n in range(1, 31)]


def _pick(choices, target, prefer_die):
    target = max(1.0, target)
    return min(choices, key=lambda nd: (abs(nd[0] * (nd[1] + 1) / 2 - target),
                                        abs(nd[1] - prefer_die), nd[0]))


def dice_for(target, prefer_die):
    """Dice for a weapon attack: a handful plus a flat bonus, never 15d8.

    Real stat blocks cap out around four dice and grow the die size instead,
    so the count is capped at four here.
    """
    return _pick(DICE_CHOICES, target, prefer_die)


def area_dice(target, prefer_die):
    """Dice for a breath weapon or other recharging blast.

    These do use long strings of dice in published creatures, so the count is
    allowed to run up.
    """
    return _pick(AREA_CHOICES, target, prefer_die)


def pattern_actions(pat):
    """Read an attack pattern.

    Numbers are swings, 'B' is a turn spent guarding, 'H' is a turn spent
    healing. The biggest number is the monster's heavy blow.
    """
    hits = [v for v in pat if not isinstance(v, str)]
    mean = sum(hits) / len(hits) if hits else 1.0
    return {
        'swings': len(hits),
        'guards': sum(1 for v in pat if v == 'B'),
        'heals': sum(1 for v in pat if v == 'H'),
        'spike': (max(hits) / mean) if hits else 1.0,
    }


def build(mon, kind):
    """One finished stat block, as a plain dict."""
    cr, pl = challenge(mon)
    t = temper(mon['hp'], mon['atk'])
    prof = proficiency(cr)
    pa = pattern_actions(mon['pat'])

    # Armor and hit points carry the shell; attack and damage carry the bite.
    # Being a boss is already paid for in the rating above, so it is not paid
    # for a second time here.
    ac = max(10, min(22, ac_target(cr) + round((t - 0.5) * 4) + kind.get('ac', 0)))
    hp_goal = hp_target(cr) * (0.80 + 0.40 * t)
    dpr = dpr_target(cr) * (1.25 - 0.50 * t)
    atk_bonus_goal = atk_target(cr) + round((0.5 - t) * 2)

    # ---- ability scores ----
    size = kind['size']
    base = 10 + round(cr * 0.5)
    prime = kind.get('prime', 'str')
    scores = {k: max(1, min(30, base + v)) for k, v in
              dict(str=0, dex=0, con=0, int=-4, wis=0, cha=-2).items()}
    for k, v in kind.get('abil', {}).items():
        scores[k] = max(1, min(30, scores[k] + v))
    scores[prime] = max(1, min(30, scores[prime] + 3))
    # Big things are strong, small things are not.
    scores['str'] = max(1, min(30, scores['str'] +
                               {'Tiny': -6, 'Small': -3, 'Medium': 0,
                                'Large': 3, 'Huge': 6, 'Gargantuan': 8}[size]))
    scores['dex'] = max(1, min(30, scores['dex'] +
                               {'Tiny': 4, 'Small': 2, 'Medium': 0,
                                'Large': -1, 'Huge': -3, 'Gargantuan': -4}[size]))

    # ---- hit points as hit dice ----
    die = SIZE_DIE[size]
    con_mod = ability_mod(scores['con'])
    n = max(1, round(hp_goal / ((die + 1) / 2 + con_mod))) if ((die + 1) / 2 + con_mod) > 0 else 1
    hp = avg(n, die, n * con_mod)

    # ---- the attack ----
    atk_abil = kind.get('atk_abil', 'str')
    atk_bonus = ability_mod(scores[atk_abil]) + prof
    # Nudge the governing score so the written bonus lands where it should.
    drift = atk_bonus_goal - atk_bonus
    if drift:
        scores[atk_abil] = max(1, min(30, scores[atk_abil] + drift * 2))
        atk_bonus = ability_mod(scores[atk_abil]) + prof

    dmg_mod = ability_mod(scores[atk_abil])
    dmg_die = kind.get('die', 6)
    # A monster whose pattern ends on a much bigger number has a heavy blow.
    # Every boss gets one: it is fought alone and needs something that changes
    # the shape of the fight.
    has_heavy = pa['spike'] >= 1.3 or mon['boss']

    # Published creatures put well under half their rated damage into ordinary
    # attacks and let the recharging blast carry the rest. Matching that is
    # what keeps these blocks looking like the real thing.
    melee_budget = dpr * (0.45 if has_heavy else 0.85)

    # A creature can only afford as many attacks as its damage will stretch to.
    # Three little hits that each add a big ability bonus would far outrun the
    # rating, so the count comes down until it fits.
    swings = min(3, max(1, pa['swings']))
    if cr < 1:
        swings = 1
    elif cr < 2:
        swings = min(2, swings)
    while swings > 1 and (dmg_mod + 2.5) * swings > melee_budget:
        swings -= 1

    dn, dmg_die = dice_for(melee_budget / swings - dmg_mod, dmg_die)

    # ---- the heavy blow ----
    heavy = None
    if has_heavy:
        hv_die = kind.get('heavy_die', 6)
        # It recharges, so it lands about a third of the time. Sized to make up
        # the part of the round's damage the ordinary attacks did not cover.
        hv_n, hv_die = area_dice(dpr * 0.65, hv_die)
        heavy = {'die': hv_die, 'n': hv_n, 'breath': kind.get('breath'),
                 'dc': 8 + prof + ability_mod(scores[kind.get('save_abil', 'con')])}

    return {
        'slug': mon['slug'], 'name': mon['name'],
        'world': mon['world'], 'world_i': mon['world_i'], 'world_id': mon['world_id'],
        'area': mon['area'], 'area_i': mon['area_i'], 'boss': mon['boss'],
        'party_level': pl, 'cr': cr, 'cr_name': cr_name(cr), 'xp': CR_XP[cr],
        'temper': round(t, 3), 'game_hp': mon['hp'], 'game_atk': mon['atk'],
        'game_lv': mon['lv'], 'pat': mon['pat'],
        'size': size, 'type': kind['type'], 'tag': kind.get('tag'),
        'align': kind.get('align', 'unaligned'),
        'ac': ac, 'ac_note': kind.get('ac_note'),
        'hp': hp, 'hit_dice': '%dd%d%s' % (n, die, (' + %d' % (n * con_mod)) if n * con_mod > 0
                                           else (' - %d' % abs(n * con_mod)) if n * con_mod < 0 else ''),
        'speed': kind.get('speed', {'walk': 30}),
        'scores': scores,
        'prof': prof,
        'saves': kind.get('saves', []),
        'skills': kind.get('skills', []),
        'senses': kind.get('senses', []),
        'languages': kind.get('langs', '—'),
        'vuln': dedupe(kind.get('vuln', [])), 'res': dedupe(kind.get('res', [])),
        'imm': dedupe(kind.get('imm', [])),
        'cond_imm': dedupe(kind.get('cond_imm', [])),
        'traits': dedupe(kind.get('traits', [])),
        'guard_key': kind.get('guard'), 'heal_key': kind.get('heal'),
        'attack': {'name': kind.get('atk_name', 'Slam'),
                   'kind': kind.get('atk_kind', 'Melee Weapon Attack'),
                   'reach': kind.get('reach'),
                   'range': kind.get('range'),
                   'bonus': atk_bonus, 'n': dn, 'die': dmg_die, 'mod': dmg_mod,
                   'dmg_type': kind.get('dmg_type', 'bludgeoning'),
                   'rider': kind.get('rider')},
        'swings': swings, 'heavy': heavy,
        'guards': pa['guards'], 'heals': pa['heals'],
        'suit': mon['off_suit'],
        'desc': kind.get('desc', ''),
        'tactics': kind.get('tactics'),
    }
