"""Reusable trait text and creature families.

Trait wording is taken from the System Reference Document 5.1, used under
CC BY 4.0. The attribution notice required by that licence is printed in the
book. {n} is replaced by the creature's name, {x} by a number worked out from
its own stats.
"""

TRAITS = {
    'pack': ('Pack Tactics',
             "The {n} has advantage on an attack roll against a creature if at least one "
             "of the {n}'s allies is within 5 feet of the creature and the ally isn't "
             "incapacitated."),
    'keen_hs': ('Keen Hearing and Smell',
                "The {n} has advantage on Wisdom (Perception) checks that rely on hearing "
                "or smell."),
    'keen_smell': ('Keen Smell',
                   "The {n} has advantage on Wisdom (Perception) checks that rely on smell."),
    'keen_sight': ('Keen Sight',
                   "The {n} has advantage on Wisdom (Perception) checks that rely on sight."),
    'echo': ('Echolocation', "The {n} can't use its blindsight while deafened."),
    'blind': ('Blind Senses',
              "The {n} can't use its blindsight while deafened and unable to smell."),
    'spiderclimb': ('Spider Climb',
                    "The {n} can climb difficult surfaces, including upside down on "
                    "ceilings, without needing to make an ability check."),
    'webwalker': ('Web Walker', "The {n} ignores movement restrictions caused by webbing."),
    'regen': ('Regeneration',
              "The {n} regains {x} hit points at the start of its turn. If the {n} takes "
              "acid or fire damage, this trait doesn't function at the start of the {n}'s "
              "next turn. The {n} dies only if it starts its turn with 0 hit points and "
              "doesn't regenerate."),
    'regen_plain': ('Regeneration',
                    "The {n} regains {x} hit points at the start of its turn if it has at "
                    "least 1 hit point."),
    'undead_fort': ('Undead Fortitude',
                    "If damage reduces the {n} to 0 hit points, it must make a Constitution "
                    "saving throw with a DC of 5 + the damage taken, unless the damage is "
                    "radiant or from a critical hit. On a success, the {n} drops to 1 hit "
                    "point instead."),
    'sunlight': ('Sunlight Sensitivity',
                 "While in sunlight, the {n} has disadvantage on attack rolls, as well as "
                 "on Wisdom (Perception) checks that rely on sight."),
    'magic_res': ('Magic Resistance',
                  "The {n} has advantage on saving throws against spells and other magical "
                  "effects."),
    'legendary': ('Legendary Resistance (3/Day)',
                  "If the {n} fails a saving throw, it can choose to succeed instead."),
    'amphib': ('Amphibious', "The {n} can breathe air and water."),
    'waterbreath': ('Water Breathing',
                    "The {n} can breathe only underwater."),
    'hold_breath': ('Hold Breath', "The {n} can hold its breath for 30 minutes."),
    'charge': ('Charge',
               "If the {n} moves at least 20 feet straight toward a target and then hits it "
               "with a melee attack on the same turn, the target takes an extra {x} damage. "
               "If the target is a creature, it must succeed on a DC {dc} Strength saving "
               "throw or be knocked prone."),
    'flyby': ('Flyby',
              "The {n} doesn't provoke an opportunity attack when it flies out of an "
              "enemy's reach."),
    'incorporeal': ('Incorporeal Movement',
                    "The {n} can move through other creatures and objects as if they were "
                    "difficult terrain. It takes 5 (1d10) force damage if it ends its turn "
                    "inside an object."),
    'false_app': ('False Appearance',
                  "While the {n} remains motionless, it is indistinguishable from its "
                  "surroundings."),
    'siege': ('Siege Monster',
              "The {n} deals double damage to objects and structures."),
    'immutable': ('Immutable Form',
                  "The {n} is immune to any spell or effect that would alter its form."),
    'magic_weapons': ('Magic Weapons', "The {n}'s weapon attacks are magical."),
    'stench': ('Stench',
               "Any creature that starts its turn within 5 feet of the {n} must succeed on "
               "a DC {dc} Constitution saving throw or be poisoned until the start of its "
               "next turn. On a successful saving throw, the creature is immune to the {n}'s "
               "Stench for 24 hours."),
    'death_burst': ('Death Burst',
                    "When the {n} dies, it explodes. Each creature within 10 feet of it "
                    "must make a DC {dc} Dexterity saving throw, taking {x} damage on a "
                    "failed save, or half as much damage on a successful one."),
    'ice_walk': ('Ice Walk',
                 "The {n} can move across and climb icy surfaces without needing to make "
                 "an ability check. Additionally, difficult terrain composed of ice or snow "
                 "doesn't cost it extra movement."),
    'snow_camo': ('Snow Camouflage',
                  "The {n} has advantage on Dexterity (Stealth) checks made to hide in "
                  "snowy terrain."),
    'sand_camo': ('Desert Camouflage',
                  "The {n} has advantage on Dexterity (Stealth) checks made to hide in "
                  "sandy terrain."),
    'swamp_camo': ('Swamp Camouflage',
                   "The {n} has advantage on Dexterity (Stealth) checks made to hide in "
                   "swampy terrain."),
    'stone_camo': ('Stone Camouflage',
                   "The {n} has advantage on Dexterity (Stealth) checks made to hide in "
                   "rocky terrain."),
    'fire_absorb': ('Fire Absorption',
                    "Whenever the {n} is subjected to fire damage, it takes no damage and "
                    "instead regains a number of hit points equal to the fire damage dealt."),
    'light_absorb': ('Lightning Absorption',
                     "Whenever the {n} is subjected to lightning damage, it takes no damage "
                     "and instead regains a number of hit points equal to the lightning "
                     "damage dealt."),
    'illumination': ('Illumination',
                     "The {n} sheds bright light in a 10-foot radius and dim light for an "
                     "additional 10 feet."),
    'turn_res': ('Turn Resistance',
                 "The {n} has advantage on saving throws against any effect that turns "
                 "undead."),
    'turn_imm': ('Turn Immunity', "The {n} is immune to effects that turn undead."),
    'nimble': ('Nimble Escape',
               "The {n} can take the Disengage or Hide action as a bonus action on each of "
               "its turns."),
    'blood_frenzy': ('Blood Frenzy',
                     "The {n} has advantage on melee attack rolls against any creature that "
                     "doesn't have all its hit points."),
    'standing_leap': ('Standing Leap',
                      "The {n}'s long jump is up to 20 feet and its high jump up to 10 feet, "
                      "with or without a running start."),
    'rampage': ('Rampage',
                "When the {n} reduces a creature to 0 hit points with a melee attack on its "
                "turn, the {n} can take a bonus action to move up to half its speed and make "
                "one attack."),
    'reckless': ('Reckless',
                 "At the start of its turn, the {n} can gain advantage on all melee weapon "
                 "attack rolls it makes during that turn, but attack rolls against it have "
                 "advantage until the start of its next turn."),
    'devils_sight': ("Devil's Sight",
                     "Magical darkness doesn't impede the {n}'s darkvision."),
    'two_heads': ('Two Heads',
                  "The {n} has advantage on Wisdom (Perception) checks and on saving throws "
                  "against being blinded, charmed, deafened, frightened, stunned, and "
                  "knocked unconscious."),
    'earth_glide': ('Earth Glide',
                    "The {n} can burrow through nonmagical, unworked earth and stone. While "
                    "doing so, it doesn't disturb the material it moves through."),
    'air_form': ('Air Form',
                 "The {n} can enter a hostile creature's space and stop there. It can move "
                 "through a space as narrow as 1 inch wide without squeezing."),
    'fire_form': ('Fire Form',
                  "The {n} can move through a space as narrow as 1 inch wide without "
                  "squeezing. A creature that touches the {n} or hits it with a melee attack "
                  "while within 5 feet of it takes {x} fire damage."),
    'ooze_amorph': ('Amorphous',
                    "The {n} can move through a space as narrow as 1 inch wide without "
                    "squeezing."),
    'spell_sunder': ('Spell Sunder',
                     "The {n} is immune to any spell of 3rd level or lower. On a failed save "
                     "against a higher-level spell, the {n} takes half damage."),
    'avoidance': ('Avoidance',
                  "If the {n} is subjected to an effect that allows it to make a saving "
                  "throw to take only half damage, it instead takes no damage if it succeeds "
                  "on the saving throw, and only half damage if it fails."),
    'horrify': ('Horrifying Visage',
                "Each non-undead creature within 60 feet of the {n} that can see it must "
                "succeed on a DC {dc} Wisdom saving throw or be frightened for 1 minute. A "
                "frightened creature can repeat the saving throw at the end of each of its "
                "turns, ending the effect on itself on a success."),
    'shapechanger': ('Shapechanger',
                     "The {n} can use its action to polymorph into a beast form, or back "
                     "into its true form. Its statistics are the same in each form. Any "
                     "equipment it is wearing or carrying isn't transformed. It reverts to "
                     "its true form if it dies."),
    'rejuvenate': ('Rejuvenation',
                   "If it is destroyed, the {n} returns in 1d10 days, restored to full hit "
                   "points, unless the anchor binding it to this place is destroyed first."),
    'swarm': ('Swarm',
              "The {n} can occupy another creature's space and vice versa, and it can move "
              "through any opening large enough for a single member of the swarm. The {n} "
              "can't regain hit points or gain temporary hit points."),
    'mimicry': ('Mimicry',
                "The {n} can mimic sounds it has heard, including voices. A creature that "
                "hears the sounds can tell they are imitations with a successful DC {dc} "
                "Wisdom (Insight) check."),
    'grappler': ('Grappler',
                 "The {n} has advantage on attack rolls against any creature it is "
                 "grappling."),
    'fey_charm': ('Fey Presence',
                  "Any creature charmed by the {n} is also beguiled by its words, and has "
                  "disadvantage on Wisdom (Insight) checks made against it."),
    'tunneler': ('Tunneler',
                 "The {n} can burrow through solid rock at half its burrow speed and leaves "
                 "a 10-foot-diameter tunnel in its wake."),
    'relentless': ('Relentless (Recharges after a Short or Long Rest)',
                   "If the {n} takes {x} damage or less that would reduce it to 0 hit "
                   "points, it is reduced to 1 hit point instead."),
    'aura_fire': ('Heated Body',
                  "A creature that touches the {n} or hits it with a melee attack while "
                  "within 5 feet of it takes {x} fire damage."),
    'aura_cold': ('Freezing Body',
                  "A creature that touches the {n} or hits it with a melee attack while "
                  "within 5 feet of it takes {x} cold damage."),
}

# What a turn spent guarding ('B' in the attack pattern) becomes at the table.
GUARDS = {
    'parry': ('Parry', 'reaction',
              "The {n} adds 2 to its AC against one melee attack that would hit it. To do "
              "so, the {n} must see the attacker and be wielding a melee weapon."),
    'shield': ('Shield Wall', 'reaction',
               "The {n} adds 3 to its AC against one attack that would hit it. To do so, "
               "the {n} must see the attacker and be wielding a shield."),
    'harden': ('Harden', 'bonus action',
               "The {n} sets itself and gains resistance to bludgeoning, piercing, and "
               "slashing damage until the start of its next turn. While hardened, its speed "
               "is 0."),
    'shell': ('Dig In', 'bonus action',
              "The {n} hunkers behind its shell. Until the start of its next turn, it has "
              "+4 AC and its speed is 0."),
    'coil': ('Coil', 'bonus action',
             "The {n} draws itself in. Until the start of its next turn, it has +3 AC and "
             "attack rolls it makes have disadvantage."),
    'ward': ('Warding Gesture', 'bonus action',
             "The {n} wraps itself in a shimmering ward and gains {x} temporary hit points."),
    'wings': ('Wing Guard', 'bonus action',
              "The {n} folds its wings over itself. Until the start of its next turn, it "
              "has +3 AC and cannot fly."),
}

# What a turn spent healing ('H' in the attack pattern) becomes at the table.
HEALS = {
    'drain': ('Life Drain', 'action',
              "Melee Weapon Attack: {atk} to hit, reach 5 ft., one creature. Hit: {x} "
              "necrotic damage. The target must succeed on a DC {dc} Constitution saving "
              "throw or its hit point maximum is reduced by an amount equal to the damage "
              "taken. This reduction lasts until the creature finishes a long rest. The {n} "
              "regains hit points equal to the damage dealt."),
    'feed': ('Feed', 'action',
             "The {n} bites one creature it is grappling. The target takes {x} piercing "
             "damage and the {n} regains that many hit points."),
    'regen': ('regen', None, None),           # use the Regeneration trait instead
    'regen_plain': ('regen_plain', None, None),
    'mend': ('Mend', 'bonus action',
             "The {n} knits itself back together and regains {x} hit points."),
    'prayer': ('Dark Prayer', 'bonus action',
               "The {n} regains {x} hit points, or one ally it can see within 30 feet "
               "regains that many instead."),
    'siphon': ('Siphon', 'bonus action',
               "One creature the {n} can see within 30 feet must succeed on a DC {dc} "
               "Constitution saving throw or take {x} necrotic damage. The {n} regains hit "
               "points equal to the damage dealt."),
    'bloom': ('Bloom', 'bonus action',
              "Roots and new growth close the {n}'s wounds. It regains {x} hit points."),
    'ember': ('Stoke', 'bonus action',
              "The {n} draws on its own fire and regains {x} hit points. Until the end of "
              "its next turn, its melee attacks deal an extra 1d6 fire damage."),
}

# ---------------------------------------------------------------------------
# Families. A creature names one and overrides what makes it itself.
# ---------------------------------------------------------------------------
FAMILIES = {
    'beast_brute': dict(
        size='Large', type='beast', align='unaligned', prime='str', atk_abil='str',
        atk_name='Bite', dmg_type='piercing', die=8, speed={'walk': 40},
        skills=['Perception'], traits=['keen_smell'], guard='shell', heal='regen_plain'),
    'beast_fast': dict(
        size='Medium', type='beast', align='unaligned', prime='dex', atk_abil='dex',
        atk_name='Bite', dmg_type='piercing', die=6, speed={'walk': 40},
        skills=['Perception', 'Stealth'], traits=['keen_hs'], guard='shell',
        heal='regen_plain'),
    'beast_flyer': dict(
        size='Small', type='beast', align='unaligned', prime='dex', atk_abil='dex',
        atk_name='Bite', dmg_type='piercing', die=4, speed={'walk': 5, 'fly': 60},
        skills=['Perception'], traits=['flyby'], guard='wings', heal='regen_plain'),
    'vermin': dict(
        size='Medium', type='beast', align='unaligned', prime='dex', atk_abil='dex',
        atk_name='Bite', dmg_type='piercing', die=6, speed={'walk': 30, 'climb': 30},
        skills=['Stealth'], traits=['spiderclimb'], guard='coil', heal='regen_plain'),
    'humanoid_soldier': dict(
        size='Medium', type='humanoid', align='lawful evil', prime='str', atk_abil='str',
        atk_name='Longsword', dmg_type='slashing', die=8, speed={'walk': 30},
        ac=2, ac_note='chain mail, shield', skills=['Athletics'],
        langs='Common', saves=[], guard='shield', heal='mend'),
    'humanoid_rogue': dict(
        size='Medium', type='humanoid', align='neutral evil', prime='dex', atk_abil='dex',
        atk_name='Scimitar', dmg_type='slashing', die=6, speed={'walk': 30},
        ac=1, ac_note='studded leather', skills=['Stealth', 'Deception'],
        langs='Common', traits=['nimble'], guard='parry', heal='mend'),
    'humanoid_caster': dict(
        size='Medium', type='humanoid', align='neutral evil', prime='cha', atk_abil='cha',
        atk_name='Withering Touch', atk_kind='Melee Spell Attack', dmg_type='necrotic',
        die=8, speed={'walk': 30}, skills=['Arcana'], langs='Common',
        abil={'int': 4, 'cha': 2}, save_abil='cha', guard='ward', heal='prayer'),
    'undead_shambler': dict(
        size='Medium', type='undead', align='neutral evil', prime='str', atk_abil='str',
        atk_name='Slam', dmg_type='bludgeoning', die=6, speed={'walk': 25},
        senses=['darkvision 60 ft.'], imm=['poison'], cond_imm=['poisoned'],
        traits=['undead_fort'], langs="understands the languages it knew in life but can't speak",
        guard='harden', heal='drain'),
    'undead_spirit': dict(
        size='Medium', type='undead', align='chaotic evil', prime='cha', atk_abil='cha',
        atk_name='Chilling Touch', atk_kind='Melee Spell Attack', dmg_type='cold',
        die=8, speed={'walk': 0, 'fly': 40}, senses=['darkvision 60 ft.'],
        res=['acid', 'fire', 'lightning', 'thunder',
             'bludgeoning, piercing, and slashing from nonmagical attacks'],
        imm=['cold', 'necrotic', 'poison'],
        cond_imm=['charmed', 'exhaustion', 'grappled', 'paralyzed', 'petrified',
                  'poisoned', 'prone', 'restrained'],
        traits=['incorporeal'], langs='Common', abil={'cha': 2},
        guard='ward', heal='siphon'),
    'undead_knight': dict(
        size='Medium', type='undead', align='lawful evil', prime='str', atk_abil='str',
        atk_name='Longsword', dmg_type='slashing', die=8, speed={'walk': 30},
        ac=3, ac_note='plate', senses=['darkvision 120 ft.'],
        imm=['necrotic', 'poison'], cond_imm=['exhaustion', 'frightened', 'poisoned'],
        traits=['magic_weapons'], langs='Common', guard='parry', heal='drain'),
    'construct': dict(
        size='Large', type='construct', align='unaligned', prime='str', atk_abil='str',
        atk_name='Slam', dmg_type='bludgeoning', die=8, speed={'walk': 30},
        senses=['darkvision 60 ft.'], imm=['poison', 'psychic'],
        cond_imm=['charmed', 'exhaustion', 'frightened', 'paralyzed', 'petrified', 'poisoned'],
        traits=['immutable'], langs="understands its maker's orders but can't speak",
        guard='harden', heal='mend'),
    'fiend': dict(
        size='Medium', type='fiend', align='chaotic evil', prime='str', atk_abil='str',
        atk_name='Claws', dmg_type='slashing', die=6, speed={'walk': 30},
        senses=['darkvision 120 ft.'], res=['cold', 'lightning'],
        imm=['fire', 'poison'], cond_imm=['poisoned'],
        traits=['devils_sight', 'magic_res'], langs='Abyssal, telepathy 120 ft.',
        guard='parry', heal='feed'),
    'giant': dict(
        size='Huge', type='giant', align='chaotic evil', prime='str', atk_abil='str',
        atk_name='Greatclub', dmg_type='bludgeoning', die=8, speed={'walk': 40},
        ac=1, ac_note='hide armor', skills=['Athletics', 'Perception'],
        langs='Giant', guard='harden', heal='mend'),
    'dragonkin': dict(
        size='Large', type='dragon', align='chaotic evil', prime='str', atk_abil='str',
        atk_name='Bite', dmg_type='piercing', die=10, speed={'walk': 40, 'fly': 80},
        senses=['blindsight 10 ft.', 'darkvision 60 ft.'],
        skills=['Perception', 'Stealth'], langs='Common, Draconic',
        guard='wings', heal='mend'),
    'elemental': dict(
        size='Large', type='elemental', align='neutral', prime='dex', atk_abil='dex',
        atk_name='Slam', dmg_type='bludgeoning', die=8, speed={'walk': 0, 'fly': 90},
        imm=['poison'],
        cond_imm=['exhaustion', 'grappled', 'paralyzed', 'petrified', 'poisoned',
                  'prone', 'restrained', 'unconscious'],
        res=['bludgeoning, piercing, and slashing from nonmagical attacks'],
        langs='Primordial', traits=['air_form'], guard='ward', heal='mend'),
    'fey': dict(
        size='Medium', type='fey', align='neutral evil', prime='cha', atk_abil='cha',
        atk_name='Thorn Lash', atk_kind='Melee Spell Attack', dmg_type='piercing',
        die=6, speed={'walk': 30}, senses=['darkvision 60 ft.'],
        skills=['Perception', 'Stealth'], langs='Elvish, Sylvan',
        traits=['magic_res'], abil={'cha': 2}, guard='ward', heal='bloom'),
    'plant': dict(
        size='Huge', type='plant', align='neutral evil', prime='str', atk_abil='str',
        atk_name='Slam', dmg_type='bludgeoning', die=10, speed={'walk': 20},
        vuln=['fire'], res=['bludgeoning', 'piercing'], imm=['poison'],
        cond_imm=['exhaustion', 'poisoned'], senses=['blindsight 60 ft.'],
        langs='Sylvan', traits=['false_app'], guard='harden', heal='bloom'),
    'ooze': dict(
        size='Large', type='ooze', align='unaligned', prime='con', atk_abil='str',
        atk_name='Pseudopod', dmg_type='acid', die=8, speed={'walk': 20, 'climb': 20},
        senses=['blindsight 60 ft. (blind beyond this radius)'],
        imm=['acid', 'poison'],
        cond_imm=['blinded', 'charmed', 'deafened', 'exhaustion', 'frightened', 'prone'],
        langs='—', traits=['ooze_amorph'], guard='harden', heal='mend'),
    'monstrosity': dict(
        size='Large', type='monstrosity', align='unaligned', prime='str', atk_abil='str',
        atk_name='Bite', dmg_type='piercing', die=10, speed={'walk': 30},
        senses=['darkvision 60 ft.'], skills=['Perception'], langs='—',
        guard='harden', heal='regen_plain'),
    'aberration': dict(
        size='Large', type='aberration', align='chaotic evil', prime='str', atk_abil='str',
        atk_name='Tentacle', dmg_type='bludgeoning', die=8, speed={'walk': 20},
        senses=['darkvision 120 ft.'], res=['cold', 'psychic'],
        langs='Deep Speech, telepathy 120 ft.', traits=['magic_res'],
        guard='harden', heal='siphon'),
    'swarm_kind': dict(
        size='Medium', type='beast', align='unaligned', prime='dex', atk_abil='dex',
        atk_name='Bites', dmg_type='piercing', die=4, speed={'walk': 30},
        res=['bludgeoning', 'piercing', 'slashing'],
        cond_imm=['charmed', 'frightened', 'grappled', 'paralyzed', 'petrified',
                  'prone', 'restrained', 'stunned'],
        langs='—', traits=['swarm'], guard='coil', heal='regen_plain'),
    'sea_beast': dict(
        size='Large', type='beast', align='unaligned', prime='str', atk_abil='str',
        atk_name='Bite', dmg_type='piercing', die=10, speed={'walk': 0, 'swim': 50},
        senses=['blindsight 30 ft.'], skills=['Perception'], langs='—',
        traits=['waterbreath'], guard='coil', heal='regen_plain'),
    'celestial_fallen': dict(
        size='Large', type='celestial', align='neutral evil', prime='cha', atk_abil='cha',
        atk_name='Searing Touch', atk_kind='Melee Spell Attack', dmg_type='radiant',
        die=8, speed={'walk': 30, 'fly': 60}, senses=['truesight 60 ft.'],
        res=['radiant'], imm=['fire'], cond_imm=['charmed', 'frightened'],
        langs='Celestial, Common', traits=['magic_res'], abil={'cha': 3},
        guard='ward', heal='prayer'),
}


def family(name, **over):
    """A family, with this creature's own changes laid over it."""
    out = {k: (list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v)
           for k, v in FAMILIES[name].items()}
    for k, v in over.items():
        if k == 'traits_add':
            out.setdefault('traits', []).extend(v)
        elif k == 'res_add':
            out.setdefault('res', []).extend(v)
        elif k == 'imm_add':
            out.setdefault('imm', []).extend(v)
        elif k == 'skills_add':
            out.setdefault('skills', []).extend(v)
        elif k == 'speed_add':
            out.setdefault('speed', {}).update(v)
        elif k == 'cond_add':
            out.setdefault('cond_imm', []).extend(v)
        else:
            out[k] = v
    return out
