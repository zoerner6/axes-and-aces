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
#
# These are the Dungeon Master's Guide's own Monster Statistics by Challenge
# Rating figures, midpoint of each band. They are not a style choice. A
# challenge rating is only worth printing if it means the same thing here as
# it does in every other book at the table: a DM spends an XP budget to build
# an encounter, and the XP comes from the rating. A creature carrying CR 18
# numbers under a CR 22 label makes that arithmetic lie.
#
# cr -> (hit points, armor class, attack bonus, damage a round)
DMG_TABLE = {
    0: (3, 13, 3, 1), 0.125: (21, 13, 3, 2.5), 0.25: (42, 13, 3, 4.5),
    0.5: (60, 13, 3, 7), 1: (78, 13, 3, 11.5), 2: (93, 13, 3, 17.5),
    3: (108, 13, 4, 23.5), 4: (123, 14, 5, 29.5), 5: (138, 15, 6, 35.5),
    6: (153, 15, 6, 41.5), 7: (168, 15, 6, 47.5), 8: (183, 16, 7, 53.5),
    9: (198, 16, 7, 59.5), 10: (213, 17, 7, 65.5), 11: (228, 17, 8, 71.5),
    12: (243, 17, 8, 77.5), 13: (258, 18, 8, 83.5), 14: (273, 18, 8, 89.5),
    15: (288, 18, 8, 95.5), 16: (303, 18, 9, 101.5), 17: (318, 19, 10, 107.5),
    18: (333, 19, 10, 113.5), 19: (348, 19, 10, 119.5), 20: (378, 19, 10, 131.5),
    21: (423, 19, 11, 149.5), 22: (468, 19, 11, 167.5), 23: (513, 19, 11, 185.5),
    24: (558, 19, 12, 203.5), 25: (603, 19, 12, 221.5), 26: (648, 19, 12, 239.5),
    27: (693, 19, 13, 257.5), 28: (738, 19, 13, 275.5), 29: (783, 19, 13, 293.5),
    30: (828, 19, 14, 311.5),
}


def _row(cr):
    return DMG_TABLE[cr if cr in DMG_TABLE else snap_cr(cr)]


# Hit points are the one column of that table not taken at face value.
#
# At the top it describes published creatures well: the DMG wants 446-490 at
# CR 22 and the SRD's ancient blue dragon has 481. At the bottom it does not
# come close. It wants 50-70 at CR 1/2, where the SRD's orc has 15, its black
# bear 19 and its worg 26 — the table's low rows count armor and resistances
# as though they were hit points, and taken literally they produce a 67-point
# zombie that a 1st-level party needs four rounds to put down, ten times over
# in a single room.
#
# So this column follows published creatures where the two disagree and the
# table where they agree, converging on it from CR 13 up. Armor class, attack
# bonus and damage are the DMG's own.
HP_TARGET = {
    0: 4, 0.125: 10, 0.25: 18, 0.5: 28, 1: 42, 2: 60, 3: 78, 4: 96, 5: 114,
    6: 132, 7: 150, 8: 168, 9: 186, 10: 204, 11: 222, 12: 240, 13: 256,
    14: 272, 15: 288, 16: 303, 17: 318, 18: 333, 19: 348, 20: 378, 21: 423,
    22: 468, 23: 513, 24: 558, 25: 603, 26: 648, 27: 693, 28: 738, 29: 783,
    30: 828,
}


def hp_target(cr):
    return HP_TARGET[cr if cr in HP_TARGET else snap_cr(cr)]


def ac_target(cr):
    return _row(cr)[1]


def atk_target(cr):
    return _row(cr)[2]


def dpr_target(cr):
    """Damage a round, averaged over the first three rounds of the fight."""
    return _row(cr)[3]


# How much of a round's damage each thing actually delivers.
#
# A Recharge 5-6 blow is not free: used on the first round and then recharging
# on a 5 or 6, it lands about four rounds in seven, so a blow written to be
# worth a third of the budget only pays out a fifth of it. Sizing it as though
# it fired every round is what left the old numbers short.
RECHARGE_RATE = 0.57

# A boss's three legendary actions a round are damage too, and the DMG counts
# them. One of the three options is an attack, so a fifth of the budget is set
# aside for it rather than being spent twice.
LEGENDARY_SHARE = 0.20


def proficiency(cr):
    return 2 + max(0, (max(1, int(cr + 0.999)) - 1) // 4)


# Which saving throws a creature of each kind is proficient in, best first.
# Taken from how the SRD's own creatures of that type are written: an undead
# guards its will and its unlife, a construct its body, a dragon nearly
# everything.
SAVE_BY_TYPE = {
    'aberration': ['con', 'int', 'wis'],
    'beast': ['con', 'str', 'dex'],
    'celestial': ['wis', 'cha', 'con'],
    'construct': ['con', 'str', 'dex'],
    'dragon': ['dex', 'con', 'wis', 'cha'],
    'elemental': ['con', 'dex', 'str'],
    'fey': ['wis', 'cha', 'dex'],
    'fiend': ['cha', 'con', 'wis', 'dex'],
    'giant': ['con', 'str', 'wis'],
    'humanoid': ['con', 'wis', 'dex'],
    'monstrosity': ['con', 'dex', 'wis'],
    'ooze': ['con'],
    'plant': ['con', 'wis'],
    'undead': ['wis', 'cha', 'con'],
}

SAVE_LABEL = {'str': 'Str', 'dex': 'Dex', 'con': 'Con', 'int': 'Int',
              'wis': 'Wis', 'cha': 'Cha'}


def save_count(cr, boss):
    """How many saving throws this creature is proficient in.

    The SRD gives its weakest creatures none at all, and its legendary ones
    three or four. A boss here is fought alone against a whole party, so it
    needs its will guarded well before the rank and file do.
    """
    if boss:
        return 2 if cr < 5 else 3 if cr < 11 else 4
    if cr < 5:
        return 0
    return 2 if cr < 11 else 3


def saving_throws(cr, ctype, boss, prime, scores, prof):
    """The creature's saving throw line, already worked out.

    A boss always guards Wisdom and Constitution whatever its kind: without
    them it is banished or dominated on the first round and the fight that
    the whole area builds up to never happens.
    """
    n = save_count(cr, boss)
    if not n:
        return []
    order = list(SAVE_BY_TYPE.get(ctype, ['con', 'wis', 'dex']))
    if boss:
        for must in ('wis', 'con'):
            if must in order:
                order.remove(must)
            order.insert(0, must)
    if prime in order:
        order.remove(prime)
        order.insert(1 if boss else 0, prime)
    chosen = order[:n]
    # Print them in the usual Str-Dex-Con-Int-Wis-Cha order, not pick order.
    chosen.sort(key=['str', 'dex', 'con', 'int', 'wis', 'cha'].index)
    return ['%s %s' % (SAVE_LABEL[k], mod_str(prof + ability_mod(scores[k])))
            for k in chosen]


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
    # the shape of the fight. So does anything with a breath weapon declared —
    # a dragon that cannot breathe is not a dragon.
    has_heavy = pa['spike'] >= 1.3 or mon['boss'] or kind.get('breath')

    # Split the round's damage between the ordinary attacks, the recharging
    # blow and (for a boss) its legendary attack, so that what the creature
    # actually delivers over three rounds adds up to what its rating promises.
    # Published creatures put well under half the total into ordinary attacks
    # and let the big blow carry the rest, which is what this keeps.
    left = dpr
    if mon['boss']:
        left -= dpr * LEGENDARY_SHARE
    if has_heavy:
        heavy_delivers = left * 0.42
        melee_budget = left - heavy_delivers
    else:
        melee_budget = left

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
        # Sized so that what it pays out across the fight, once the recharge
        # is accounted for, is the share of the round the ordinary attacks
        # were not given.
        hv_n, hv_die = area_dice(heavy_delivers / RECHARGE_RATE, hv_die)
        heavy = {'die': hv_die, 'n': hv_n, 'breath': kind.get('breath'),
                 'dc': 8 + prof + ability_mod(scores[kind.get('save_abil', 'con')])}

    # ---- saving throws ----
    # Worked out last, because the attack above nudges the governing ability
    # score and a saving throw written before that would print the wrong
    # number. A creature may still name its own saves and keep them.
    saves = kind.get('saves') or saving_throws(
        cr, kind['type'], mon['boss'], prime, scores, prof)

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
        'saves': saves,
        'skills': dedupe(kind.get('skills', [])),
        'senses': dedupe(kind.get('senses', [])),
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


# ---------------------------------------------------------------------------
# Encounter building.
#
# The book gives every creature a party level and a rating and then has to say
# how to spend them, or the ratings are decoration. These are the DMG's own
# adventuring-day numbers: the XP a single character of each level can absorb
# at each difficulty, and the multiplier that makes a crowd worse than the sum
# of its parts.
# ---------------------------------------------------------------------------

# level -> (easy, medium, hard, deadly) XP, per character
THRESHOLDS = {
    1: (25, 50, 75, 100), 2: (50, 100, 150, 200), 3: (75, 150, 225, 400),
    4: (125, 250, 375, 500), 5: (250, 500, 750, 1100),
    6: (300, 600, 900, 1400), 7: (350, 750, 1100, 1700),
    8: (450, 900, 1400, 2100), 9: (550, 1100, 1600, 2400),
    10: (600, 1200, 1900, 2800), 11: (800, 1600, 2400, 3600),
    12: (1000, 2000, 3000, 4500), 13: (1100, 2200, 3400, 5100),
    14: (1250, 2500, 3800, 5700), 15: (1400, 2800, 4300, 6400),
    16: (1600, 3200, 4800, 7200), 17: (2000, 3900, 5900, 8800),
    18: (2100, 4200, 6300, 9500), 19: (2400, 4900, 7300, 10900),
    20: (2800, 5700, 8500, 12700),
}

DIFFICULTY = ('easy', 'medium', 'hard', 'deadly')


def crowd_multiplier(n):
    """A crowd hits harder than its XP says. DMG encounter multipliers."""
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.5
    if n <= 6:
        return 2.0
    if n <= 10:
        return 2.5
    if n <= 14:
        return 3.0
    return 4.0


def rate_encounter(members, party_level, party_size=4):
    """(adjusted XP, difficulty word) for a list of stat blocks."""
    raw = sum(b['xp'] for b in members)
    adj = raw * crowd_multiplier(len(members))
    lo, med, hard, deadly = THRESHOLDS[max(1, min(20, party_level))]
    budget = [lo * party_size, med * party_size, hard * party_size,
              deadly * party_size]
    word = 'trivial'
    for i, cut in enumerate(budget):
        if adj >= cut:
            word = DIFFICULTY[i]
    return int(adj), word


def suggest_encounters(mobs, boss, party_level, party_size=4):
    """Two encounters for one area: a patrol, and the boss fight.

    The patrol is grown one creature at a time until it reaches hard, which
    is where a fight stops being a speed bump. The boss is given company only
    if it is too soft on its own.
    """
    out = []
    if mobs:
        pick, i = [], 0
        while len(pick) < 12:
            cand = pick + [mobs[i % len(mobs)]]
            adj, word = rate_encounter(cand, party_level, party_size)
            pick = cand
            i += 1
            if word in ('hard', 'deadly'):
                break
        out.append(('Patrol', pick) + rate_encounter(pick, party_level, party_size))
    if boss:
        group = [boss]
        adj, word = rate_encounter(group, party_level, party_size)
        if word not in ('hard', 'deadly') and mobs:
            group = [boss, mobs[0], mobs[0]]
        out.append(('Boss fight', group) + rate_encounter(group, party_level,
                                                          party_size))
    return out
