"""Legendary actions, lair actions and spellcasting.

Every boss in this book is written to be fought alone, and a lone creature
with one turn against four or five characters loses on action economy long
before its hit points matter. Legendary actions are what the SRD's own solo
creatures use to answer that, so the bosses here use them too.

Three legendary actions a round: a cheap one, an attack for two, and
something that changes the board for three. The expensive option is chosen by
creature type, so a dragon does not fight like a golem.

Wording follows SRD 5.1 (CC BY 4.0). {n} is the creature's name, {dc} its
save DC, {xl} a damage figure worked out from its own rating.
"""

LEGENDARY_INTRO = (
    "The {n} can take 3 legendary actions, choosing from the options below. "
    "Only one legendary action can be used at a time, and only at the end of "
    "another creature's turn. The {n} regains spent legendary actions at the "
    "start of its turn.")

# The one-cost option. Anything that flies would rather reposition.
CHEAP_FLY = ('Move', "The {n} moves up to its speed without provoking "
                     "opportunity attacks.")
CHEAP_GROUND = ('Detect', "The {n} makes a Wisdom (Perception) check.")

# The three-cost option, by creature type.
BIG = {
    'dragon': ('Wing Attack',
               "The {n} beats its wings. Each creature within 15 feet of it must "
               "succeed on a DC {dc} Dexterity saving throw or take {xl} bludgeoning "
               "damage and be knocked prone. The {n} can then move up to half its "
               "speed."),
    'beast': ('Pounce',
              "The {n} moves up to its speed and makes one attack. If the target is "
              "Large or smaller, it must succeed on a DC {dc} Strength saving throw "
              "or be knocked prone."),
    'monstrosity': ('Thrash',
                    "The {n} lashes out at everything near it. Each creature within "
                    "10 feet of it must succeed on a DC {dc} Dexterity saving throw "
                    "or take {xl} damage."),
    'undead': ('Withering Gaze',
               "The {n} fixes one creature it can see within 60 feet. That creature "
               "must succeed on a DC {dc} Constitution saving throw or take {xl} "
               "necrotic damage, and its hit point maximum is reduced by the same "
               "amount until it finishes a long rest."),
    'construct': ('Shockwave',
                  "The {n} slams the ground. Each creature within 15 feet of it must "
                  "succeed on a DC {dc} Strength saving throw or take {xl} "
                  "bludgeoning damage and be knocked prone."),
    'fiend': ('Scorching Glare',
              "The {n} turns its full attention on one creature it can see within 60 "
              "feet. That creature must succeed on a DC {dc} Dexterity saving throw "
              "or take {xl} fire damage."),
    'giant': ('Stomp',
              "The {n} brings a foot down. Each creature within 10 feet of it must "
              "succeed on a DC {dc} Dexterity saving throw or take {xl} bludgeoning "
              "damage and be knocked prone."),
    'elemental': ('Surge',
                  "The {n} sweeps through the space of every creature within 15 feet "
                  "of it. Each of them must succeed on a DC {dc} Strength saving "
                  "throw or take {xl} damage and be pushed 10 feet away."),
    'fey': ('Beguile',
            "One creature the {n} can see within 30 feet must succeed on a DC {dc} "
            "Wisdom saving throw or use its reaction to move up to its speed in a "
            "direction of the {n}'s choosing."),
    'celestial': ('Radiant Burst',
                  "Light breaks off the {n}. Each creature within 15 feet of it must "
                  "succeed on a DC {dc} Constitution saving throw or take {xl} "
                  "radiant damage and be blinded until the end of its next turn."),
    'plant': ('Entangling Growth',
              "Roots erupt around one creature the {n} can see within 30 feet. That "
              "creature must succeed on a DC {dc} Strength saving throw or be "
              "restrained until the end of its next turn."),
    'humanoid': ('Rallying Shout',
                 "The {n} calls out. Each ally within 30 feet of it that can hear it "
                 "may immediately move up to half its speed or make one weapon "
                 "attack."),
    'aberration': ('Warping Pulse',
                   "Space folds around the {n}. Each creature within 10 feet of it "
                   "must succeed on a DC {dc} Wisdom saving throw or take {xl} "
                   "psychic damage."),
    'ooze': ('Engulfing Surge',
             "The {n} flows over one creature within 5 feet of it. That creature must "
             "succeed on a DC {dc} Dexterity saving throw or take {xl} acid damage."),
}


def actions_for(b):
    """The three legendary options for one boss, as (name, cost, text)."""
    flies = b['speed'].get('fly', 0) > 0
    cheap = CHEAP_FLY if flies else CHEAP_GROUND
    big = BIG.get(b['type'], BIG['monstrosity'])
    atk = b['attack']['name']
    return [
        (cheap[0], 1, cheap[1]),
        (atk, 2, "The {n} makes one %s attack." % atk.lower()),
        (big[0], 3, big[1]),
    ]


# ---------------------------------------------------------------------------
# Lair actions, for the creature that ends a world.
#
# Ten of the forty bosses are the last thing in their world, and every one of
# those worlds is a named, described place. That is what lair actions are for,
# and the locations were already written.
# ---------------------------------------------------------------------------

LAIRS = {
    'w1': ("the cellars and back rooms beneath the inn", 13, [
        "A flagstone tilts underfoot. Each creature standing on stone within 20 feet "
        "of the {n} must succeed on a DC {ld} Dexterity saving throw or fall prone.",
        "Every candle and lantern within 60 feet gutters out. That area is dark until "
        "the end of the {n}'s next turn.",
        "Rats pour out of the walls. One creature the {n} can see within 30 feet must "
        "succeed on a DC {ld} Dexterity saving throw or take 5 (2d4) piercing damage."]),
    'w2': ("the high passes and the ice fields below them", 14, [
        "Ice spreads across the ground in a 20-foot square. That area is difficult "
        "terrain until the end of the {n}'s next turn.",
        "Wind drives the snow flat. Until the end of the {n}'s next turn, ranged "
        "attacks made more than 10 feet from the target have disadvantage.",
        "Ice falls from overhead. One creature the {n} can see must succeed on a DC "
        "{ld} Dexterity saving throw or take 7 (2d6) cold damage."]),
    'w3': ("the dunes and the city buried under them", 15, [
        "Sand swallows the ground in a 20-foot square. That area is difficult terrain "
        "until the end of the {n}'s next turn.",
        "Heat rises off the stone. Each creature within 20 feet of the {n} must "
        "succeed on a DC {ld} Constitution saving throw or take 7 (2d6) fire damage.",
        "Grit fills the air. Until the end of the {n}'s next turn, ranged attacks "
        "against it have disadvantage."]),
    'w4': ("the drowned coast and its wreck fields", 16, [
        "Water surges through the fight. Each creature within 20 feet of the {n} must "
        "succeed on a DC {ld} Strength saving throw or be pushed 10 feet and knocked "
        "prone.",
        "A cold current runs through. Each creature within 20 feet of the {n} has its "
        "speed halved until the end of the {n}'s next turn.",
        "The sea closes overhead. The area within 30 feet of the {n} is lightly "
        "obscured until the end of its next turn."]),
    'w5': ("the marsh and the village sunk into it", 16, [
        "The ground gives way. One creature within 30 feet of the {n} must succeed on "
        "a DC {ld} Strength saving throw or be restrained by mud until it escapes.",
        "Marsh gas rolls across the ground. Each creature within 20 feet of the {n} "
        "must succeed on a DC {ld} Constitution saving throw or be poisoned until the "
        "end of its next turn.",
        "Something rotten surfaces nearby. One creature the {n} can see must succeed "
        "on a DC {ld} Wisdom saving throw or be frightened until the end of its next "
        "turn."]),
    'w6': ("the mines and the deep galleries", 17, [
        "The roof shifts. Each creature within 20 feet of the {n} must succeed on a "
        "DC {ld} Dexterity saving throw or take 10 (3d6) bludgeoning damage.",
        "Every light within 60 feet dies for a moment. That area is heavily obscured "
        "until the end of the {n}'s next turn.",
        "A cart breaks loose and runs the gallery. Each creature in its path must "
        "succeed on a DC {ld} Dexterity saving throw or take 10 (3d6) bludgeoning "
        "damage."]),
    'w7': ("the abbey, its cloisters and its crypt", 18, [
        "The dead stir in the walls. One creature within 30 feet of the {n} must "
        "succeed on a DC {ld} Wisdom saving throw or be frightened until the end of "
        "its next turn.",
        "Grave cold fills the room. Each creature within 20 feet of the {n} must "
        "succeed on a DC {ld} Constitution saving throw or take 10 (3d6) necrotic "
        "damage.",
        "Every door in the abbey slams and holds. No creature can leave the {n}'s "
        "chamber until the end of its next turn."]),
    'w8': ("the thorn wood and the old groves", 19, [
        "Thorns erupt in a 20-foot square. That area is difficult terrain, and a "
        "creature that enters it takes 7 (2d6) piercing damage.",
        "The trees close ranks. The area within 30 feet of the {n} is lightly "
        "obscured until the end of its next turn.",
        "Roots take hold. One creature within 30 feet of the {n} must succeed on a DC "
        "{ld} Strength saving throw or be restrained until the end of its next turn."]),
    'w9': ("the sky fortress and the bridges between its towers", 19, [
        "The wind turns. Each creature within 30 feet of the {n} must succeed on a DC "
        "{ld} Strength saving throw or be pushed 15 feet.",
        "Lightning walks the stonework. One creature the {n} can see must succeed on "
        "a DC {ld} Dexterity saving throw or take 14 (4d6) lightning damage.",
        "A span of bridge drops away. Each creature standing on it must succeed on a "
        "DC {ld} Dexterity saving throw or fall."]),
    'w10': ("the Abyss itself", 20, [
        "The ground turns to something that was recently alive. The area within 30 "
        "feet of the {n} is difficult terrain until the end of its next turn.",
        "Fire wells up from below. Each creature within 20 feet of the {n} must "
        "succeed on a DC {ld} Dexterity saving throw or take 14 (4d6) fire damage.",
        "The Abyss takes an interest. One creature the {n} can see within 60 feet "
        "must succeed on a DC {ld} Wisdom saving throw or be frightened until the end "
        "of its next turn."]),
}


def lair_for(b):
    """(place, dc, [effects]) if this creature ends its world, else None."""
    return LAIRS.get(b['world_id']) if b.get('world_boss') else None


# ---------------------------------------------------------------------------
# Spellcasting.
#
# Nine creatures in this book are named and described as spellcasters. Every
# spell below is SRD 5.1. Lists are kept short on purpose: a DM running a
# fight wants the three or four spells the creature will actually cast, not a
# wizard's whole book.
# ---------------------------------------------------------------------------

# slug -> (class word, casting ability, spell level, {level: [spells]})
SPELLCASTERS = {
    'witch': ('the 2nd-level spellcaster', 'cha', 2, {
        0: ['chill touch', 'poison spray', 'prestidigitation'],
        1: ['charm person', 'ray of sickness'],
    }),
    'frostmage': ('the 3rd-level spellcaster', 'wis', 3, {
        0: ['ray of frost', 'resistance', 'thaumaturgy'],
        1: ['bane', 'fog cloud'],
        2: ['hold person'],
    }),
    'priest': ('the 5th-level spellcaster', 'wis', 5, {
        0: ['light', 'sacred flame', 'thaumaturgy'],
        1: ['bane', 'inflict wounds', 'shield of faith'],
        2: ['hold person', 'spiritual weapon'],
        3: ['bestow curse', 'dispel magic'],
    }),
    'seawitch': ('the 6th-level spellcaster', 'cha', 6, {
        0: ['chill touch', 'ray of frost', 'shocking grasp'],
        1: ['fog cloud', 'witch bolt'],
        2: ['hold person', 'misty step'],
        3: ['lightning bolt'],
    }),
    'icequeen': ('the 7th-level spellcaster', 'cha', 7, {
        0: ['chill touch', 'ray of frost', 'mage hand'],
        1: ['fog cloud', 'shield'],
        2: ['hold person', 'misty step'],
        3: ['sleet storm'],
        4: ['ice storm'],
    }),
    'darkpriest': ('the 9th-level spellcaster', 'wis', 9, {
        0: ['sacred flame', 'spare the dying', 'thaumaturgy'],
        1: ['bane', 'inflict wounds'],
        2: ['blindness/deafness', 'silence'],
        3: ['animate dead', 'bestow curse'],
        4: ['blight'],
        5: ['contagion'],
    }),
    'elfmage': ('the 10th-level spellcaster', 'int', 10, {
        0: ['druidcraft', 'poison spray', 'shocking grasp'],
        1: ['entangle', 'faerie fire'],
        2: ['barkskin', 'spike growth'],
        3: ['plant growth', 'lightning bolt'],
        4: ['blight'],
        5: ['insect plague'],
    }),
    'demonmage': ('the 12th-level spellcaster', 'cha', 12, {
        0: ['fire bolt', 'mage hand', 'minor illusion'],
        1: ['burning hands', 'shield'],
        2: ['darkness', 'misty step'],
        3: ['fireball', 'counterspell'],
        4: ['wall of fire'],
        5: ['cone of cold'],
        6: ['chain lightning'],
    }),
    'lich': ('the 15th-level spellcaster', 'int', 15, {
        0: ['chill touch', 'mage hand', 'prestidigitation', 'ray of frost'],
        1: ['detect magic', 'magic missile', 'shield'],
        2: ['blindness/deafness', 'mirror image'],
        3: ['animate dead', 'counterspell', 'fireball'],
        4: ['blight', 'dimension door'],
        5: ['cloudkill', 'scrying'],
        6: ['disintegrate', 'globe of invulnerability'],
        7: ['finger of death', 'plane shift'],
    }),
}

SLOTS = {
    2: {1: 3}, 3: {1: 4, 2: 2}, 5: {1: 4, 2: 3, 3: 2},
    6: {1: 4, 2: 3, 3: 3}, 7: {1: 4, 2: 3, 3: 3, 4: 1},
    9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
}

ORDINAL = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th',
           7: '7th', 8: '8th', 9: '9th'}
