"""Creatures of worlds 8, 9 and 10."""
from families import family as F

KINDS = {}

# ===========================================================================
# World 8 - The Elven Wilds
# ===========================================================================
KINDS.update({
    'thornelf': F('humanoid_rogue', align='neutral evil', tag='elf',
                  atk_name='Thorn Bow', atk_kind='Ranged Weapon Attack',
                  range='150/600 ft.', dmg_type='piercing', die=8,
                  langs='Elvish, Common', senses=['darkvision 60 ft.'],
                  skills=['Perception', 'Stealth', 'Survival'],
                  traits_add=['magic_res'], rider='poison',
                  desc="She has held this treeline for three hundred years and the "
                       "thorn has gotten into her. She will not ask you to leave twice.",
                  tactics="Shoots from cover at long range and moves after every shot."),
    'wolfpack': F('beast_fast', size='Large', atk_name='Antlers',
                  dmg_type='piercing', die=10, speed={'walk': 50},
                  traits_add=['charge', 'keen_hs'], res_add=['necrotic'],
                  desc="A stag the color of a shadow with a rack like a hedge of "
                       "spears. It is not a deer any more.",
                  tactics="Charges out of the trees, then away, and comes back around."),
    'pixie': F('fey', size='Tiny', align='chaotic evil', atk_name='Needle',
               atk_kind='Melee Weapon Attack', dmg_type='piercing', die=4,
               speed={'walk': 10, 'fly': 40}, prime='dex', atk_abil='dex',
               traits_add=['flyby', 'magic_res'], heal='bloom',
               skills_add=['Stealth'], langs='Sylvan',
               desc="Hand-sized, delighted with itself, and entirely out of patience "
                    "with people. The wood has turned it cruel.",
               tactics="Flits in, jabs, and is twenty feet up before you look."),
    'thornbear': F('beast_brute', size='Huge', type='monstrosity',
                   align='neutral evil', atk_name='Claws', dmg_type='slashing',
                   die=10, ac=2, ac_note='briar hide', res_add=['piercing'],
                   traits_add=['keen_smell', 'legendary'], guard='harden',
                   heavy_die=10, heal='bloom',
                   desc="A bear the briar grew through and kept. The thorns are part "
                        "of it now and they come away in you.",
                   tactics="Sets its feet and makes you come into the thorns to reach "
                           "it."),

    'dryad': F('fey', size='Medium', align='neutral evil', atk_name='Vine Whip',
               atk_kind='Melee Weapon Attack', dmg_type='bludgeoning', die=6,
               traits_add=['magic_res', 'fey_charm'], heal='bloom',
               skills_add=['Nature'], rider='grapple',
               desc="Her tree is sick and she has decided it is your fault. She may "
                    "even be right.",
               tactics="Talks first, charms whoever listens, and sets the wood on the "
                       "rest."),
    'werewolf': F('humanoid_soldier', size='Medium', type='monstrosity',
                  align='chaotic evil', atk_name='Claws', dmg_type='slashing',
                  die=8, ac=1, ac_note='natural armor', speed={'walk': 40},
                  res_add=['bludgeoning, piercing, and slashing from nonmagical '
                           'attacks that are not silvered'],
                  traits_add=['keen_hs', 'shapechanger'], langs='Common',
                  skills_add=['Perception'], heal='regen_plain', guard='parry',
                  desc="Perfectly reasonable for most of the month. This is not most "
                       "of the month.",
                  tactics="Fights as a wolf, and ordinary steel barely troubles it."),
    'mushroomman': F('plant', size='Large', atk_name='Fist', die=8,
                     traits_add=['stench', 'false_app'], guard='harden',
                     heal='bloom', rider='poison', langs='—',
                     desc="Grown up out of the glade floor overnight, shoulder-high "
                          "and shaped roughly like a man. The spores are the problem.",
                     tactics="Stands in the middle of you and bursts when it drops."),
    'unicorn': F('celestial_fallen', size='Large', align='chaotic evil',
                 atk_name='Horn', atk_kind='Melee Weapon Attack',
                 dmg_type='piercing', die=10, speed={'walk': 50},
                 prime='str', atk_abil='str', imm=['poison'], res=['radiant'],
                 cond_imm=['charmed', 'paralyzed', 'poisoned'],
                 traits_add=['magic_res', 'legendary', 'charge'], heal='prayer',
                 langs='Celestial, Elvish, Sylvan', heavy_die=10,
                 desc="It was the glade's guardian and the thorn got into it too. It "
                      "is still beautiful, which makes it worse.",
                 tactics="Charges, and mends itself out of whatever it has just run "
                         "through."),

    'elfknight': F('humanoid_soldier', align='lawful evil', tag='elf',
                   atk_name='Thornblade', dmg_type='slashing', die=8, ac=3,
                   ac_note='living bark plate', langs='Elvish, Common',
                   senses=['darkvision 60 ft.'], traits_add=['magic_res'],
                   guard='parry', rider='poison', skills_add=['Perception'],
                   desc="Armored in bark that grew to fit and will not come off. He "
                        "holds the old city gate out of habit.",
                   tactics="Parries properly, waits for your mistake, and punishes it "
                           "once."),
    'elfmage': F('humanoid_caster', align='neutral evil', tag='elf', prime='int',
                 atk_abil='int', atk_name='Bramble Bolt',
                 atk_kind='Ranged Spell Attack', range='120 ft.',
                 dmg_type='piercing', die=6, abil={'int': 5}, save_abil='int',
                 langs='Elvish, Common', senses=['darkvision 60 ft.'],
                 traits_add=['magic_res'], heal='bloom',
                 skills=['Arcana', 'Nature', 'Perception'],
                 desc="She has been studying the thorn for a century and has stopped "
                      "being able to tell her work from herself.",
                 tactics="Grows cover between you and her, keeps the knights up, and "
                         "never closes."),
    'owlbear': F('monstrosity', size='Large', atk_name='Claws',
                 dmg_type='slashing', die=10, speed={'walk': 40},
                 traits_add=['keen_hs', 'rampage'], heavy_die=10,
                 desc="Owl at the top, bear underneath, foul temper throughout. It "
                      "has been living in the ruins since the elves left.",
                 tactics="One target at a time, and it moves on to the next the "
                         "moment the first goes down."),
    'elfgeneral': F('humanoid_soldier', align='lawful evil', tag='elf',
                    atk_name='Briar Glaive', dmg_type='slashing', die=10,
                    ac=3, ac_note='thornplate', reach='10 ft.',
                    langs='Elvish, Common', senses=['darkvision 60 ft.'],
                    traits_add=['magic_res', 'legendary'], guard='parry',
                    heavy_die=10, skills_add=['Perception', 'Athletics'],
                    desc="He gave the order that let the thorn in and has spent the "
                         "years since insisting it was correct. The city agrees with "
                         "him now.",
                    tactics="Keeps you at ten feet, guards the one blow that would "
                            "land, and answers with three."),

    'thornbeast': F('plant', size='Large', atk_name='Thorn Lash', die=8,
                    reach='15 ft.', traits_add=['false_app'], guard='harden',
                    heal='bloom', rider='grapple', langs='—',
                    desc="The briar made something that walks. It is all thorn and "
                         "no thought.",
                    tactics="Reaches fifteen feet and drags people into the bank of "
                            "thorns."),
    'vinesnake': F('plant', size='Large', atk_name='Constrict',
                   dmg_type='bludgeoning', die=8, speed={'walk': 30, 'climb': 30},
                   traits_add=['false_app', 'grappler'], rider='grapple',
                   guard='coil', heal='bloom', langs='—',
                   desc="It hangs with the other vines until one of them moves. Then "
                        "it is around your chest.",
                   tactics="Grabs one person and squeezes, ignoring everything else."),
    'rootgolem': F('construct', size='Huge', type='plant', atk_name='Root Fist',
                   die=10, ac=2, ac_note='heartwood',
                   vuln=['fire'], res=['bludgeoning', 'piercing'],
                   imm=['poison'], cond_imm=['exhaustion', 'poisoned'],
                   traits=['siege', 'false_app'], guard='harden', heal='bloom',
                   langs='Sylvan', heavy_die=10,
                   desc="The Heart Tree put out a limb and the limb got up. It is "
                        "built of the oldest wood in the wood.",
                   tactics="Blocks the way to the tree and heals as long as the tree "
                           "stands."),
    'thornqueen': F('fey', size='Medium', align='neutral evil', prime='cha',
                    atk_abil='cha', atk_name='Thorn Crown',
                    atk_kind='Melee Spell Attack', dmg_type='piercing', die=10,
                    ac=3, ac_note='briar ward',
                    traits_add=['magic_res', 'legendary', 'fey_charm'],
                    heal='bloom', skills_add=['Deception', 'Insight', 'Perception'],
                    langs='Elvish, Sylvan, Common', heavy_die=10,
                    desc="She is the thorn, and the Thorned Heart is her. She has been "
                         "waiting under the tree for someone to come and argue about "
                         "it.",
                    tactics="Charms one of you to fight for her, and the Heart Tree "
                            "mends her every turn it is still standing."),
})

# ===========================================================================
# World 9 - The Sky Fortress
# ===========================================================================
KINDS.update({
    'harpy': F('monstrosity', size='Medium', align='chaotic evil',
               atk_name='Talons', dmg_type='slashing', die=6,
               speed={'walk': 20, 'fly': 60}, prime='dex', atk_abil='dex',
               traits_add=['flyby', 'mimicry'], langs='Common',
               skills_add=['Perception'], res_add=['lightning'],
               desc="It nests under the cloud bridges and sings at whoever is "
                    "crossing. The storm covers the noise of the rest of them.",
               tactics="Sings from below the bridge and takes whoever leans over."),
    'cloudgiant': F('giant', traits_add=['standing_leap'], size='Large', align='neutral evil',
                    atk_name='Fist', die=10, res_add=['lightning', 'thunder'],
                    ac=0, ac_note='hide', guard='harden',
                    desc="Not a proper cloud giant, just big and bad-tempered and up "
                         "very high. It throws what it is standing on.",
                    tactics="Hurls lumps of cloudstuff, then wades in."),
    'windspirit': F('elemental', size='Medium', atk_name='Gust',
                    dmg_type='bludgeoning', die=6, traits=['air_form', 'flyby'],
                    res_add=['lightning', 'thunder'], heal='mend',
                    desc="You cannot see it, only what it is doing to the bridge "
                         "ropes. It wants you over the edge, not dead.",
                    tactics="Shoves rather than strikes, and the fall does the rest."),
    'griffon': F('monstrosity', size='Large', atk_name='Beak',
                 dmg_type='piercing', die=10, speed={'walk': 30, 'fly': 80},
                 ac=1, ac_note='natural armor', traits_add=['keen_sight', 'flyby',
                                                            'legendary'],
                 guard='wings', heavy_die=10, skills_add=['Perception'],
                 desc="Eagle in front, lion behind, and king of everything that flies "
                      "between the bridges. The nests up here are all his family.",
                 tactics="Never lands. Takes one of you off the bridge and drops them."),

    'skyserpent': F('dragonkin', traits_add=['flyby'], size='Large', atk_name='Bite', die=10,
                    speed={'walk': 10, 'fly': 70}, ac=1, ac_note='natural armor',
                    res_add=['lightning'], breath='lightning', heavy_die=8,
                    desc="It swims through the air between the gardens and is longer "
                         "than the bridge. Mostly it is left alone.",
                    tactics="Circles the garden out of reach and comes through it "
                            "once, lengthwise."),
    'thunderbird': F('beast_flyer', size='Large', atk_name='Talons',
                     dmg_type='slashing', die=8, speed={'walk': 20, 'fly': 80},
                     imm=['lightning'], traits_add=['flyby', 'light_absorb',
                                                    'keen_sight'],
                     rider='lightning', heal='mend',
                     desc="The storm follows it rather than the other way round. Every "
                          "beat of the wings cracks.",
                     tactics="Dives through the group trailing lightning and climbs out."),
    'gardenguard': F('construct', size='Large', atk_name='Stone Fist', die=10,
                     ac=2, ac_note='natural armor', traits_add=['false_app', 'siege'],
                     guard='harden', heal='mend',
                     desc="One of the statues along the garden path, and nobody has "
                          "counted them lately. It steps down when you pass.",
                     tactics="Waits for the group to spread out along the path, then "
                             "blocks the middle."),
    'stormdrake': F('dragonkin', size='Huge', atk_name='Bite', die=12, ac=3,
                    ac_note='natural armor', imm=['lightning'], res_add=['thunder'],
                    breath='lightning', heavy_die=8,
                    traits_add=['legendary', 'light_absorb'],
                    senses=['blindsight 30 ft.', 'darkvision 120 ft.'],
                    desc="It keeps the gardens and the weather over them and takes "
                         "lightning as a compliment. The Storm Titan's own beast.",
                    tactics="Hovers, empties its lungs down the length of the garden, "
                            "and feeds on anyone who answers with lightning."),

    'stormsoldier': F('humanoid_soldier', traits_add=['nimble'], align='lawful evil', atk_name='Storm Pike',
                      dmg_type='piercing', die=8, ac=3, ac_note='plate, shield',
                      reach='10 ft.', res_add=['lightning'], rider='lightning',
                      guard='shield', langs='Common, Primordial',
                      desc="He has stood this wall long enough that the storm has got "
                           "into the armor. The pike carries it.",
                      tactics="Holds the line at ten feet and will not break formation."),
    'airelemental': F('elemental', size='Large', atk_name='Slam',
                      dmg_type='bludgeoning', die=8, traits=['air_form', 'flyby'],
                      res_add=['lightning', 'thunder'], heal='mend',
                      desc="A piece of the storm with a shape to it, pulled in to "
                          "walk the walls. It is the wall's weather now.",
                      tactics="Picks a target up off the parapet and takes them over "
                              "the side."),
    'djinnwarrior': F('elemental', size='Large', align='lawful evil',
                      atk_name='Cloud Scimitar', atk_kind='Melee Weapon Attack',
                      dmg_type='slashing', die=8, prime='cha', atk_abil='cha',
                      traits_add=['magic_res', 'air_form'], heal='siphon',
                      langs='Primordial, Common', skills_add=['Perception'],
                      desc="Bound to the fortress by an old bargain and deeply tired "
                           "of it. It fights well anyway.",
                      tactics="Mends itself on the way in and fights in the air where "
                              "you cannot follow."),
    'stormgiant': F('giant', size='Huge', align='neutral evil', atk_name='Greatsword',
                    dmg_type='slashing', die=12, ac=2, ac_note='stormplate',
                    imm=['lightning'], res_add=['thunder', 'cold'],
                    traits_add=['legendary', 'light_absorb'], guard='harden',
                    heavy_die=10, langs='Giant, Common',
                    skills_add=['Athletics', 'Perception'],
                    desc="He holds the wall for the Titan and does it properly. "
                         "Lightning is weather to him, nothing more.",
                    tactics="Two swings and a third that takes the parapet with it. "
                            "Lightning only makes him stronger."),

    'thunderknight': F('humanoid_soldier', traits_add=['relentless'], align='lawful evil',
                       atk_name='Thunder Maul', dmg_type='bludgeoning', die=10,
                       ac=4, ac_note='plate, shield', imm=['lightning'],
                       res_add=['thunder'], rider='thunder', guard='shield',
                       langs='Common, Primordial', skills_add=['Athletics'],
                       heavy_die=10,
                       desc="Last rank before the throne, and the best of them. Every "
                            "blow lands twice, once as the hit and once as the noise.",
                       tactics="Shields the first attack and then brings the maul down "
                               "with the thunder behind it."),
    'stormwraith': F('undead_spirit', atk_name='Storm Touch', dmg_type='lightning',
                     die=8, imm=['lightning', 'cold', 'necrotic', 'poison'],
                     traits_add=['light_absorb', 'horrify'], heal='siphon',
                     desc="Someone who went off the fortress wall and never finished "
                          "falling. It is part of the storm now.",
                     tactics="Comes through the throne room wall, frightens the group "
                             "apart, and drains the stragglers."),
    'rocbird': F('beast_flyer', size='Gargantuan', atk_name='Beak',
                 dmg_type='piercing', die=12, speed={'walk': 20, 'fly': 120},
                 ac=1, ac_note='natural armor', traits_add=['keen_sight', 'flyby'],
                 heavy_die=10, guard='wings',
                 desc="Big enough that its shadow is the first warning and the second "
                      "is already too late. It nests above the throne.",
                 tactics="Takes one person in each foot and climbs."),
    'stormtitan': F('giant', size='Gargantuan', align='chaotic evil',
                    atk_name='Lightning Glaive', dmg_type='lightning', die=12,
                    ac=3, ac_note='titanplate', reach='15 ft.',
                    imm=['lightning', 'thunder'], res_add=['cold'],
                    traits_add=['legendary', 'light_absorb', 'siege'],
                    guard='harden', heavy_die=12, langs='Giant, Common, Primordial',
                    skills_add=['Athletics', 'Perception'],
                    desc="He sat down on the Storm Throne and the weather has done "
                         "what he says ever since. He has been expecting you for some "
                         "time.",
                    tactics="Keeps you at fifteen feet, and when you bunch up he calls "
                            "the whole storm down on the floor."),
})

# ===========================================================================
# World 10 - The Abyss
# ===========================================================================
KINDS.update({
    'hellhound': F('fiend', size='Large', atk_name='Bite', dmg_type='fire',
                   die=8, speed={'walk': 50}, traits_add=['pack', 'keen_smell',
                                                          'aura_fire'],
                   heal='feed', langs='understands Infernal but cannot speak',
                   desc="It hunts the ash wastes in threes and the ash does not slow "
                        "it. The bite comes out the other side still burning.",
                   tactics="Runs the group down and cuts off whoever falls behind."),
    'imp2': F('fiend', size='Small', atk_name='Searing Claws', dmg_type='fire',
              die=6, speed={'walk': 30, 'fly': 50}, traits_add=['flyby',
                                                                'aura_fire'],
              heal='ember', langs='Infernal, Common',
              desc="One of a great many, and the only reason it is dangerous is that "
                   "there is never one. It is on fire and pleased about it.",
              tactics="Swarms in the air and keeps out of reach of anything slow."),
    'ashghoul': F('undead_shambler', align='chaotic evil', atk_name='Claws',
                  dmg_type='slashing', die=8, res_add=['fire'],
                  traits_add=['undead_fort', 'sand_camo'], heal='feed',
                  cond_add=['charmed'],
                  desc="It lies down in the ash until something walks past. Everything "
                       "out here is the same gray.",
                  tactics="Rises underfoot in a group and pins one person to feed."),
    'cerberus': F('fiend', size='Large', atk_name='Bite', dmg_type='fire',
                  die=10, speed={'walk': 50}, ac=2, ac_note='natural armor',
                  traits_add=['two_heads', 'keen_smell', 'aura_fire', 'legendary'],
                  guard='harden', heavy_die=10,
                  langs='understands Infernal but cannot speak',
                  desc="Three heads, one very poor temper, and the job of keeping "
                       "things in rather than out. You are going the wrong way.",
                  tactics="Bites with all three and cannot be flanked or surprised."),

    'chaindemon': F('fiend', size='Large', atk_name='Barbed Chain',
                    dmg_type='slashing', die=8, reach='15 ft.',
                    traits_add=['devils_sight'], rider='grapple', heal='feed',
                    desc="Wrapped in the chains it used to be in charge of. It fights "
                         "at the length of them.",
                    tactics="Hooks someone at fifteen feet and drags them off alone."),
    'succubus': F('fiend', size='Medium', align='neutral evil', prime='cha',
                  atk_abil='cha', atk_name='Shadow Touch',
                  atk_kind='Melee Spell Attack', dmg_type='necrotic', die=8,
                  speed={'walk': 30, 'fly': 60}, traits_add=['magic_res',
                                                             'shapechanger'],
                  heal='siphon', skills_add=['Deception', 'Insight', 'Perception'],
                  langs='Abyssal, Common, telepathy 60 ft.',
                  desc="It will be whoever you would rather be fighting, right up "
                       "until it is not. The halls are full of people it convinced.",
                  tactics="Wears a friendly face, turns one of you, and drains them "
                          "when they are no longer useful."),
    'jailer': F('fiend', size='Large', atk_name='Iron Key', dmg_type='bludgeoning',
                die=10, ac=3, ac_note='pitted plate', guard='harden',
                heal='feed', skills_add=['Intimidation', 'Perception'],
                desc="It has kept these halls locked for longer than the halls have "
                     "existed. It is not interested in why you came.",
                tactics="Shuts the door behind you and sets itself in front of it."),
    'warden': F('fiend', size='Huge', atk_name='Pit Maul', dmg_type='bludgeoning',
                die=12, ac=3, ac_note='natural armor',
                traits_add=['legendary', 'siege', 'devils_sight'],
                guard='harden', heavy_die=10,
                desc="Whatever is in the deepest of these cells, the Warden is what "
                     "keeps it there. That ought to tell you something.",
                tactics="Takes the whole party's first round, hardens, and then starts "
                        "swinging."),

    'lavaserpent': F('monstrosity', size='Huge', atk_name='Bite', dmg_type='fire',
                     die=12, speed={'walk': 30, 'swim': 50},
                     imm=['fire'], traits_add=['fire_absorb', 'aura_fire',
                                               'illumination'],
                     heal='ember', heavy_die=10, langs='—',
                     senses=['blindsight 60 ft.', 'darkvision 120 ft.'],
                     desc="It swims the lake the way an eel swims a river, and the "
                          "lake is fire. It surfaces for air it does not need.",
                     tactics="Comes out of the lake at whoever is nearest the shore."),
    'firegiant': F('giant', size='Huge', align='lawful evil', atk_name='Greatsword',
                   dmg_type='fire', die=12, ac=2, ac_note='blackened plate',
                   imm=['fire'], traits_add=['aura_fire'], guard='harden',
                   heavy_die=10, langs='Giant',
                   skills_add=['Athletics', 'Perception'],
                   desc="He forges on the shore of the lake and has made most of what "
                        "the Abyss fights with. The hammer is also the sword.",
                   tactics="Plants himself and swings. Fire is not going to help you."),
    'phoenix': F('celestial_fallen', size='Large', align='chaotic evil',
                 atk_name='Burning Talons', atk_kind='Melee Weapon Attack',
                 dmg_type='fire', die=10, speed={'walk': 20, 'fly': 90},
                 prime='dex', atk_abil='dex', imm=['fire'],
                 traits_add=['fire_absorb', 'illumination', 'flyby', 'death_burst'],
                 heal='ember', heavy_die=8,
                 desc="It burns black instead of gold and comes back anyway. Killing "
                      "it is the start of the problem.",
                 tactics="Fights in the air, and when it drops it takes the ground "
                         "around it with it."),
    'balrog': F('fiend', size='Huge', atk_name='Flame Lash', dmg_type='fire',
                die=12, reach='15 ft.', ac=2, ac_note='natural armor',
                speed={'walk': 40, 'fly': 60}, imm=['fire', 'poison'],
                traits_add=['legendary', 'aura_fire', 'illumination', 'magic_weapons'],
                heal='ember', heavy_die=10,
                desc="It is the biggest thing on the lake shore and the fire comes off "
                     "it in sheets. The Demon King keeps it as a doorman.",
                tactics="Holds you at fifteen feet with the lash and burns anyone who "
                        "closes."),

    'demonknight': F('fiend', size='Large', atk_name='Abyssal Blade',
                     dmg_type='slashing', die=10, ac=4, ac_note='plate, shield',
                     traits_add=['magic_weapons', 'devils_sight'], guard='shield',
                     heal='feed', skills_add=['Athletics'], heavy_die=10,
                     desc="Last rank before the throne, in armor made on the lake "
                          "shore. It has never been asked to retreat.",
                     tactics="Shields the first blow, then two of its own and a third "
                             "with everything behind it."),
    'abyssbeast': F('aberration', size='Huge', atk_name='Tentacle',
                    dmg_type='bludgeoning', die=10, reach='15 ft.', ac=2,
                    ac_note='natural armor', res_add=['fire'],
                    traits_add=['magic_res', 'devils_sight'], rider='grapple',
                    heal='siphon', heavy_die=10,
                    desc="Nobody built this and nobody summoned it. It was here before "
                         "the throne and does not acknowledge it.",
                    tactics="Grapples two of you at fifteen feet and pulls them into "
                            "the dark."),
    'demonmage': F('fiend', size='Medium', align='chaotic evil', prime='cha',
                   atk_abil='cha', atk_name='Abyssal Bolt',
                   atk_kind='Ranged Spell Attack', range='120 ft.',
                   dmg_type='fire', die=8, traits_add=['magic_res', 'devils_sight'],
                   heal='siphon', skills_add=['Arcana', 'Deception'],
                   langs='Abyssal, Common, telepathy 120 ft.',
                   desc="It does the King's reading for him and has its own ideas "
                        "about the throne. Not yet, though.",
                   tactics="Stays at the back of the hall, keeps the knights standing, "
                           "and burns whoever gets through."),
    'demonking': F('fiend', size='Gargantuan', align='chaotic evil',
                   atk_name='Ruinous Claws', dmg_type='slashing', die=12,
                   reach='15 ft.', ac=4, ac_note='natural armor',
                   imm=['fire', 'poison'], res_add=['cold', 'lightning', 'necrotic'],
                   traits_add=['legendary', 'magic_weapons', 'aura_fire',
                               'devils_sight', 'siege'],
                   guard='harden', heal='feed', heavy_die=12,
                   langs='all, telepathy 120 ft.',
                   senses=['truesight 120 ft.'],
                   skills_add=['Insight', 'Intimidation', 'Perception'],
                   desc="Everything in the other nine worlds was working for him, "
                        "whether it knew it or not. He is the last thing in the book "
                        "and he is sitting down.",
                   tactics="Guards, then three strikes a turn, and he does not stand "
                           "up until the second half of the fight."),
})
