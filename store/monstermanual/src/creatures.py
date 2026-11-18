"""The 168 creatures, keyed by the art slug they use.

Each one names a family and changes what makes it itself. `desc` is what a
games master reads out; `tactics` is how it fights.
"""
from families import family as F

KINDS = {}

# ===========================================================================
# World 1 - The Rescue of Anna
# ===========================================================================
KINDS.update({
    'goblin': F('humanoid_rogue', size='Small', tag='goblinoid', align='neutral evil',
                atk_name='Rusty Shortsword', die=6, langs='Common, Goblin',
                senses=['darkvision 60 ft.'], skills=['Stealth'],
                desc="Knee-high, mean, and far too pleased with itself. It fights "
                     "dirty because fighting fair has never once worked for it.",
                tactics="Opens from cover, stabs whoever looks softest, and runs the "
                        "moment the fight stops being funny."),
    'rat': F('vermin', size='Small', atk_name='Bite', die=4, speed={'walk': 30},
             traits=['pack'], skills_add=['Perception'],
             desc="A rat the size of a dog, raised on cellar scraps and spite. There "
                  "is never only one.",
             tactics="Swarms the nearest ankle. Loses interest if something bigger "
                     "starts bleeding."),
    'bat': F('beast_flyer', size='Tiny', atk_name='Bite', die=4,
             senses=['blindsight 60 ft.'], traits_add=['echo'],
             desc="It lives in the tavern rafters and resents company. All leather "
                  "and teeth and bad temper.",
             tactics="Dives, bites an ear, and is back in the dark before anyone "
                     "swings."),
    'boar': F('beast_brute', size='Medium', atk_name='Tusk', die=6,
              traits_add=['charge', 'relentless'],
              desc="Someone let a boar into the tavern. It has knocked over three "
                   "tables and is not finished.",
              tactics="Picks a target, lowers its head, and does not change its mind."),
    'imp': F('fiend', size='Tiny', atk_name='Sting', dmg_type='piercing', die=4,
             speed={'walk': 20, 'fly': 40}, traits_add=['flyby'],
             heal='feed', langs='Infernal, Common',
             desc="A hand-sized devil with a grin it has not earned. It is here "
                  "because somebody summoned it and then lost interest.",
             tactics="Stays airborne, stings, and licks the wound to mend its own."),
    'bandit': F('humanoid_rogue', size='Medium', align='neutral evil',
                atk_name='Cutlass', die=8, ac=2, ac_note='studded leather, shield',
                skills_add=['Intimidation'], guard='shield',
                desc="The one giving the orders, and the only one in the room who "
                     "has thought past tonight. He took Anna because she was worth "
                     "something to someone.",
                tactics="Keeps a table between himself and you, lets his men tire you "
                        "out, then opens up with everything at once."),

    'skeleton': F('undead_shambler', traits_add=['false_app'], atk_name='Rusted Shortsword', dmg_type='piercing',
                  die=6, ac=1, ac_note='armor scraps', vuln=['bludgeoning'],
                  cond_add=['exhaustion'], traits=[], guard='parry', heal='mend',
                  desc="Held together by old string and worse magic. It rattles when "
                       "it walks, which is the only warning you get.",
                  tactics="Comes straight on. A good hammer blow takes most of it "
                          "apart at once."),
    'spider': F('vermin', size='Large', atk_name='Bite', dmg_type='piercing', die=8,
                speed={'walk': 30, 'climb': 30}, traits_add=['webwalker'],
                senses=['darkvision 60 ft.'], rider='poison',
                desc="Big enough to need the whole corner of the cellar for its web. "
                     "It has been waiting a long time.",
                tactics="Drops from the ceiling, bites, and backs off to let the "
                        "poison work."),
    'snake': F('beast_fast', size='Medium', atk_name='Bite', die=6,
               speed={'walk': 30, 'swim': 30}, senses=['blindsight 10 ft.'],
               rider='poison', traits=['blind'], guard='coil',
               desc="It came up through the cellar drain and decided to stay. Patient, "
                    "quiet, and quicker than it looks.",
               tactics="Holds still until something comes close, then strikes once "
                       "and withdraws."),
    'zombie': F('undead_shambler', atk_name='Slam', die=6,
                desc="Slow, dim, and very hard to put down for good. It was somebody "
                     "once and nobody has had the decency to say who.",
                tactics="Walks at you until it reaches you. Keeps getting back up."),
    'scorpion': F('vermin', size='Medium', atk_name='Sting', die=6,
                  speed={'walk': 40}, senses=['blindsight 10 ft.'], rider='poison',
                  traits=['blind'], guard='shell', ac=2, ac_note='natural armor',
                  desc="All shell and no sense. The tail is the part to watch, and "
                       "it knows it.",
                  tactics="Grabs with the claws so the sting cannot miss."),
    'ghoul': F('undead_shambler', align='chaotic evil', atk_name='Claws',
               dmg_type='slashing', die=6, speed={'walk': 30},
               imm=['poison'], cond_imm=['charmed', 'exhaustion', 'poisoned'],
               traits=['undead_fort'], heal='feed', skills=['Perception'],
               desc="It has been down here with the barrels long enough to forget "
                    "bread. It is the reason the cellar door was locked from the "
                    "outside.",
               tactics="Pins one person and feeds while the rest of the fight happens "
                       "around it."),

    'wolf': F('beast_fast', size='Large', atk_name='Bite', die=8, speed={'walk': 50},
              traits_add=['pack'],
              desc="Lean, grey, and hungry enough to try a road with four armed "
                   "people on it. It is not working alone.",
              tactics="Circles for position and only commits once something else has "
                      "your attention."),
    'witch': F('humanoid_caster', traits_add=['swamp_camo'], align='neutral evil', atk_name='Hex Bolt',
               atk_kind='Ranged Spell Attack', range='60/120 ft.', dmg_type='necrotic',
               die=8, skills=['Arcana', 'Deception'], heal='prayer',
               desc="She lives where the trees close over the path and charges a "
                    "price nobody wants to pay twice. Still polite about it.",
               tactics="Keeps her distance, mends herself first, and saves the worst "
                       "of it for whoever is nearly down."),
    'bear': F('beast_brute', size='Large', atk_name='Claws', dmg_type='slashing',
              die=8, speed={'walk': 40, 'climb': 30}, traits_add=['keen_smell'],
              desc="A bear having a bad week. You are in its wood and it has "
                   "explained that twice already.",
              tactics="One enormous swing, then another. No plan beyond that."),
    'treant': F('plant', size='Huge', atk_name='Branch', die=10,
                traits_add=['siege'], heal='bloom',
                desc="An old tree that got tired of being walked past. It moves about "
                     "as fast as you would expect and hits considerably harder.",
                tactics="Stands its ground, swings both limbs, and heals in the sun."),
    'toad': F('beast_brute', size='Large', atk_name='Bite', die=8,
              speed={'walk': 20, 'swim': 40}, traits_add=['amphib', 'standing_leap'],
              desc="A toad the size of a cart horse. It swallows things whole and "
                   "regrets nothing.",
              tactics="Leaps the gap, bites, and tries to get the smallest of you "
                      "inside its mouth."),
    'troll': F('giant', size='Large', align='chaotic evil', atk_name='Claws',
               dmg_type='slashing', die=8, speed={'walk': 30},
               senses=['darkvision 60 ft.'], traits_add=['keen_smell'],
               heal='regen', guard='harden', langs='Giant',
               desc="King of a wood with no other trolls in it, which has never "
                    "troubled him. Cut him and it closes over while you watch.",
               tactics="Wades in, takes the hits, and waits for your fire to run out."),

    'knight': F('humanoid_soldier', traits_add=['relentless'], align='lawful evil', atk_name='Greatsword',
                die=10, ac=3, ac_note='plate',
                skills_add=['Perception'], guard='parry',
                desc="Grimstone's man at arms, in armor nobody has polished in "
                     "years. He does not talk and he does not stop.",
                tactics="Fights properly: guards, waits for an opening, and puts "
                        "everything into one blow."),
    'gargoyle': F('construct', size='Medium', type='elemental', align='chaotic evil',
                  atk_name='Claws', dmg_type='slashing', die=6,
                  speed={'walk': 30, 'fly': 60},
                  res=['bludgeoning, piercing, and slashing from nonmagical attacks '
                       "that aren't adamantine"],
                  imm=['poison'], cond_imm=['exhaustion', 'petrified', 'poisoned'],
                  traits=['false_app'], langs='Terran', guard='harden', heal='mend',
                  desc="It sat on the parapet for a hundred years looking like "
                       "masonry. It was counting.",
                  tactics="Holds still until you walk under it, then drops."),
    'ghost': F('undead_spirit', atk_name='Withering Touch', dmg_type='necrotic',
               die=8, traits_add=['horrify'], heal='siphon',
               desc="Something that died in this hall and has not accepted the news. "
                    "It goes through walls and takes its time.",
               tactics="Steps out of the stone, frightens whoever is closest, and "
                       "drains the one who runs."),
    'vampire': F('undead_knight', align='lawful evil', atk_name='Bite',
                 dmg_type='piercing', die=6, ac=1, ac_note='natural armor',
                 speed={'walk': 30, 'climb': 30},
                 res=['necrotic', 'bludgeoning, piercing, and slashing from '
                      'nonmagical attacks'],
                 imm=[], cond_imm=['charmed'],
                 traits=['spiderclimb', 'sunlight'], heal='feed',
                 skills=['Deception', 'Perception', 'Stealth'],
                 desc="Well dressed, well spoken, and entirely finished with being "
                      "polite about dinner. Keep it away from the windows and it "
                      "never tires.",
                 tactics="Grapples the weakest of you and feeds. Will not follow you "
                         "into daylight."),
    'babydragon': F('dragonkin', traits_add=['keen_smell'], size='Medium', atk_name='Bite', die=8,
                    ac=2, ac_note='natural armor',
                    res_add=['fire'], heavy_die=6, breath='fire',
                    desc="Dog-sized, bad-tempered, and already convinced the castle "
                         "is its own. The fire works perfectly well.",
                    tactics="Stays out of reach, bites, and empties its lungs at "
                            "whoever bunched up."),
    'dragon': F('dragonkin', size='Huge', atk_name='Bite', die=12, ac=4,
                ac_note='natural armor', imm=['fire'], heavy_die=6, breath='fire',
                senses=['blindsight 30 ft.', 'darkvision 120 ft.'],
                skills_add=['Perception'], traits_add=['legendary'],
                desc="The reason Castle Grimstone has no roof left on the tower. It "
                     "has Anna, it knows exactly why you came, and it is in no hurry.",
                tactics="Fights from the air, lands only to bite, and burns the whole "
                        "room when you spread out."),
})

# ===========================================================================
# World 2 - The Frozen Peaks
# ===========================================================================
KINDS.update({
    'icewolf': F('beast_fast', size='Large', atk_name='Bite', die=8,
                 speed={'walk': 50}, res_add=['cold'],
                 traits_add=['pack', 'snow_camo', 'ice_walk'],
                 desc="White on white until it is already too close. The pack works "
                      "the pass like a trade.",
                 tactics="Drives you off the trail into deeper snow, then takes its "
                         "time."),
    'snowgoblin': F('humanoid_rogue', size='Small', tag='goblinoid',
                    atk_name='Ice Spear', dmg_type='piercing', die=6,
                    langs='Common, Goblin', senses=['darkvision 60 ft.'],
                    res_add=['cold'], traits_add=['snow_camo'],
                    desc="Same goblin, worse weather, and a spear of hard ice it "
                         "makes fresh every morning. Tougher than its cousins "
                         "because the soft ones died.",
                    tactics="Throws first from behind a drift, closes only when you "
                            "are already busy."),
    'frostbat': F('beast_flyer', size='Small', atk_name='Bite', die=4,
                  senses=['blindsight 60 ft.'], res_add=['cold'],
                  traits_add=['echo'], rider='cold',
                  desc="It roosts in the pass and its bite leaves the skin white. "
                       "You hear them before you see them.",
                  tactics="Comes out of the dark in numbers, bites, and is gone."),
    'yetichief': F('giant', size='Large', align='chaotic neutral', atk_name='Fist',
                   die=8, res_add=['cold'], senses=['darkvision 60 ft.'],
                   traits_add=['snow_camo', 'ice_walk', 'keen_smell'],
                   guard='harden', langs='Giant',
                   desc="Head of whatever lives above the treeline, and the only "
                        "thing up here that owns the weather. He watched you climb "
                        "the whole way.",
                   tactics="Lets the cold do half the work, plants himself across "
                           "the path, and does not move for anything."),

    'icegolem': F('construct', size='Large', atk_name='Slam', die=8,
                  imm=['poison', 'psychic', 'cold'],
                  vuln=['fire'], traits_add=['ice_walk'], ac=1,
                  ac_note='natural armor', langs='—',
                  desc="Ice shaped into arms and legs by something that is no longer "
                       "in the cave. It has forgotten why it is standing there but "
                       "not what to do about visitors.",
                  tactics="Blocks the passage and sets itself. Fire is the short way "
                          "through it."),
    'frostspider': F('vermin', size='Large', atk_name='Bite', dmg_type='piercing',
                     die=8, speed={'walk': 30, 'climb': 30}, res_add=['cold'],
                     senses=['darkvision 60 ft.'], traits_add=['webwalker', 'ice_walk'],
                     rider='cold',
                     desc="Its web is frozen stiff across the cave mouth and rings "
                          "like glass when you cut it. That is the doorbell.",
                     tactics="Waits above, drops, bites, and lets the cold slow you "
                             "down for the next one."),
    'icewraith': F('undead_spirit', atk_name='Freezing Touch', dmg_type='cold',
                   die=8, traits_add=['ice_walk'], heal='siphon',
                   desc="The breath of someone who died up here, still looking for "
                        "the way down. It is colder near it and the air does not "
                        "warm back up.",
                   tactics="Drifts through the ice wall, touches whoever is nearest, "
                           "and takes the warmth with it."),
    'icequeen': F('humanoid_caster', align='lawful evil', atk_name='Frost Lance',
                  atk_kind='Ranged Spell Attack', range='120 ft.', dmg_type='cold',
                  die=8, imm=['cold'], traits_add=['magic_res', 'ice_walk'],
                  skills=['Arcana', 'Deception', 'Perception'], heal='prayer',
                  desc="She keeps the caves the way she likes them and has had a "
                       "long time to practice. Civil right up until she is not.",
                  tactics="Opens by mending herself, freezes the ground under you, "
                          "and never once closes the distance."),

    'mammoth': F('beast_brute', size='Huge', atk_name='Tusk', die=10,
                 speed={'walk': 40}, res_add=['cold'], ac=1,
                 ac_note='natural armor', traits_add=['charge', 'siege'],
                 desc="Shaggy, armored in its own hide, and wearing somebody's war "
                      "harness. Whoever strapped it on is long gone.",
                 tactics="Builds up speed across the flat ice and goes through "
                         "whatever is in the way."),
    'icetroll': F('giant', size='Large', align='chaotic evil', atk_name='Claws',
                  dmg_type='slashing', die=8, speed={'walk': 30}, res_add=['cold'],
                  senses=['darkvision 60 ft.'], traits_add=['keen_smell', 'ice_walk'],
                  heal='regen', langs='Giant',
                  desc="A troll that found somewhere even less pleasant to live. The "
                       "cold keeps the wounds from showing and nothing stops them "
                       "closing.",
                  tactics="Takes the first round of damage on purpose to see what "
                          "you have got."),
    'seal': F('sea_beast', size='Large', atk_name='Tusk', die=8,
              speed={'walk': 20, 'swim': 50}, res_add=['cold'],
              traits=['amphib', 'hold_breath'], ac=1, ac_note='thick hide',
              desc="Half a ton of blubber and two tusks it uses like crowbars. It "
                   "owns this hole in the ice.",
              tactics="Comes up under the ice you are standing on and drags the "
                      "nearest of you down."),
    'wyrm': F('dragonkin', size='Huge', atk_name='Bite', die=12, ac=3,
              ac_note='natural armor', imm=['cold'], speed={'walk': 40, 'burrow': 30},
              heavy_die=6, breath='cold', traits_add=['ice_walk', 'tunneler'],
              senses=['blindsight 60 ft.', 'darkvision 120 ft.'],
              desc="It swims through the lake ice the way an eel swims through "
                   "water. The cracking underfoot is not the weather.",
              tactics="Surfaces beneath the group, bites, and goes back under before "
                      "you can answer."),

    'frostknight': F('humanoid_soldier', traits_add=['ice_walk'], align='lawful evil', atk_name='Frostbrand',
                     die=8, ac=3, ac_note='plate', res_add=['cold'],
                     rider='cold', guard='parry', langs='Common, Giant',
                     desc="Sworn to the Frost Giant and frozen into the job. The "
                          "armor has not come off in a very long time.",
                     tactics="Holds the doorway, parries the first real swing, and "
                             "answers it properly."),
    'giantguard': F('beast_fast', size='Large', atk_name='Bite', die=10,
                    speed={'walk': 50}, res_add=['cold'],
                    traits_add=['pack', 'keen_hs'], ac=1, ac_note='natural armor',
                    desc="The Frost Giant keeps dogs, and they are sized to match. "
                         "It has been fed just enough to stay interested.",
                    tactics="Goes for whoever is standing apart from the group."),
    'frostmage': F('humanoid_caster', traits_add=['ice_walk'], align='neutral evil', atk_name='Hailstone',
                   atk_kind='Ranged Spell Attack', range='60/120 ft.',
                   dmg_type='cold', die=6, res_add=['cold'],
                   skills=['Arcana', 'Nature'], heal='prayer', langs='Common, Giant',
                   desc="He asks the mountain for weather and the mountain answers. "
                        "That is most of his trick and it is enough.",
                   tactics="Stays behind the knights, keeps them standing, and drops "
                           "the ceiling's ice on whoever gets through."),
    'frostgiant': F('giant', size='Huge', align='neutral evil',
                    atk_name='Greataxe', dmg_type='slashing', die=12,
                    imm=['cold'], ac=2, ac_note='patchwork plate',
                    traits_add=['ice_walk', 'legendary'], guard='harden',
                    skills_add=['Athletics'],
                    desc="He took the King's Frost Crown because it was cold and it "
                         "was pretty and nobody stopped him. He is wearing it now.",
                    tactics="Two full swings a turn and a third that takes the floor "
                            "with it. No guard, no retreat."),
})

# ===========================================================================
# World 3 - The Burning Sands
# ===========================================================================
KINDS.update({
    'sandscorp': F('vermin', size='Large', atk_name='Sting', die=8,
                   speed={'walk': 40, 'burrow': 20}, senses=['blindsight 20 ft.'],
                   rider='poison', traits=['blind', 'sand_camo'], guard='shell',
                   ac=2, ac_note='natural armor',
                   desc="It spends the day under the sand and comes up through it. "
                        "The shell turns most things you will swing at it.",
                   tactics="Erupts under one of you, grabs with the claws, and "
                           "stings until it lets go."),
    'vulture': F('beast_flyer', size='Medium', atk_name='Beak', die=6,
                 speed={'walk': 10, 'fly': 60}, traits_add=['keen_sight', 'pack'],
                 skills_add=['Perception'],
                 desc="It has been following you since the second dune and is in no "
                      "rush. It does not need you dead, only slow.",
                 tactics="Circles out of reach and only comes down for someone who "
                         "has stopped moving."),
    'raider': F('humanoid_rogue', size='Medium', atk_name='Curved Blade',
                die=6, ac=1, ac_note='wrapped leathers',
                langs='Common', traits_add=['sand_camo'],
                skills=['Stealth', 'Survival'],
                desc="He knows every well on this road and has poisoned two of them. "
                     "The caravan paid him for safe passage last month.",
                tactics="Hits from the dune line and backs off before you can turn, "
                        "over and over."),
    'sandwyrm': F('monstrosity', size='Huge', atk_name='Bite', die=12,
                  speed={'walk': 30, 'burrow': 40}, senses=['blindsight 60 ft.',
                                                            'tremorsense 60 ft.'],
                  traits_add=['tunneler', 'sand_camo'], guard='harden',
                  ac=2, ac_note='natural armor', heavy_die=10,
                  desc="The caravan did not get lost. It went down, all at once, in "
                       "one place, and the sand closed over the top.",
                  tactics="Tracks you by footfall, comes up under the heaviest of "
                          "you, and swallows what it can."),

    'jackal': F('humanoid_soldier', size='Medium', type='monstrosity',
                align='lawful evil', atk_name='Khopesh', dmg_type='slashing',
                die=8, ac=1, ac_note='bronze scale', senses=['darkvision 60 ft.'],
                traits_add=['pack', 'keen_smell'], langs='Common',
                desc="Jackal-headed, bronze-armored, and still standing guard over a "
                     "temple that fell down centuries ago. The orders never got "
                     "cancelled.",
                tactics="Fights in pairs and will not step off the ground it was "
                        "told to hold."),
    'cobra': F('beast_fast', size='Large', atk_name='Bite', die=6,
               speed={'walk': 30, 'climb': 20}, senses=['blindsight 10 ft.'],
               rider='poison', traits=['blind'], guard='coil',
               desc="It rears to your chest height and spreads a hood the color of "
                    "old brass. The venom is the whole argument.",
               tactics="Strikes once, hard, and gives the poison a turn to make its "
                       "case."),
    'sandgolem': F('construct', size='Large', atk_name='Slam', die=8,
                   res_add=['bludgeoning, piercing, and slashing from nonmagical '
                            'attacks'],
                   traits_add=['sand_camo', 'earth_glide'], langs='—',
                   desc="Loose sand that holds a shape because something told it to. "
                        "Blades go straight through and change nothing.",
                   tactics="Pours back together after every hit and keeps walking."),
    'djinn': F('elemental', size='Large', align='chaotic evil',
               atk_name='Scouring Wind', atk_kind='Melee Spell Attack',
               dmg_type='slashing', die=8, prime='cha', atk_abil='cha',
               traits_add=['magic_res'], heal='siphon', langs='Primordial, Common',
               desc="Bound to the ruin and bitter about every year of it. It will "
                    "offer you a deal and the deal is not good.",
               tactics="Stays in the air inside its own sandstorm, mends itself, and "
                       "flays whoever will not take the bargain."),

    'mummy': F('undead_shambler', align='lawful evil', atk_name='Rotting Fist',
               die=8, res_add=['bludgeoning, piercing, and slashing from nonmagical '
                               'attacks'],
               vuln=['fire'], cond_add=['exhaustion'], heal='drain',
               langs='the languages it knew in life',
               desc="Wrapped, dry, and awake. It was put here with instructions and "
                    "you are not on the list.",
               tactics="Walks you down, lands one withering blow, and takes back what "
                       "the blow cost it."),
    'scarab': F('swarm_kind', size='Large', atk_name='Bites', die=6,
                speed={'walk': 30, 'climb': 30, 'burrow': 20},
                senses=['blindsight 10 ft.'], traits_add=['blind'],
                desc="A crawling carpet of beetles with one big one in the middle "
                     "doing the thinking. It fills the corridor.",
                tactics="Flows over and around you. Swords find very little to cut."),
    'tombguard': F('construct', size='Large', atk_name='Stone Maul', die=10,
                   ac=2, ac_note='natural armor', traits_add=['false_app', 'siege'],
                   guard='harden',
                   desc="Carved standing in the corner holding its hammer, and it "
                        "has not moved since. It will.",
                   tactics="Lets you walk past, then blocks the way back."),
    'pharaoh': F('undead_knight', align='lawful evil', atk_name='Royal Scepter',
                 dmg_type='bludgeoning', die=8, ac=2, ac_note='gilded wrappings',
                 res_add=['bludgeoning, piercing, and slashing from nonmagical '
                          'attacks'],
                 traits_add=['magic_res', 'legendary', 'rejuvenate'], heal='drain',
                 skills=['History', 'Perception'],
                 desc="He paid a great deal to never stop being king and the deal "
                      "held. The crown is fused to the bone now.",
                 tactics="Drains the strongest of you to keep himself standing, and "
                         "comes back if you leave the tomb intact."),

    'firewisp': F('elemental', size='Small', align='neutral evil',
                  atk_name='Searing Touch', dmg_type='fire', die=6,
                  speed={'walk': 0, 'fly': 50}, imm=['fire', 'poison'],
                  traits=['fire_form', 'illumination', 'fire_absorb'],
                  langs='Ignan', heal='ember',
                  desc="A hand-sized knot of flame that drifts the temple halls "
                       "looking for something dry. It lights the room, which is the "
                       "only courtesy it offers.",
                  tactics="Comes close on purpose so that hitting it costs you."),
    'sphinx': F('monstrosity', size='Large', align='lawful neutral',
                atk_name='Claws', dmg_type='slashing', die=10,
                speed={'walk': 40, 'fly': 60}, ac=2, ac_note='natural armor',
                res_add=['bludgeoning, piercing, and slashing from nonmagical '
                         'attacks'],
                traits_add=['magic_res'], langs='Common, Sphinx',
                skills_add=['Arcana', 'History', 'Insight'], guard='wings',
                desc="It guards the door and would rather talk than fight, but it "
                     "will fight. Answer wrong and it does not ask twice.",
                tactics="Opens with a question. Fights from the air once the "
                        "conversation is over."),
    'priest': F('humanoid_caster', traits_add=['horrify'], align='lawful evil', prime='wis', atk_abil='wis',
                atk_name='Sunburn', atk_kind='Ranged Spell Attack',
                range='60 ft.', dmg_type='radiant', die=6,
                abil={'wis': 4}, save_abil='wis', skills=['Religion', 'Persuasion'],
                heal='prayer', res_add=['fire'],
                desc="He keeps the fires lit under the Scorched King and believes "
                     "every word of it. There are a lot of him.",
                tactics="Stands at the back, keeps the front rank on its feet, and "
                        "burns anyone who reaches him."),
    'sunlord': F('celestial_fallen', size='Large', align='neutral evil',
                 atk_name='Solar Blade', atk_kind='Melee Weapon Attack',
                 dmg_type='radiant', die=10, ac=2, ac_note='scorched plate',
                 traits_add=['legendary', 'illumination'], heavy_die=8,
                 skills=['Insight', 'Perception'],
                 desc="He was something bright once and the desert burned the rest "
                      "out of him. He still thinks he is doing the right thing.",
                 tactics="Two blade strikes a turn, then a flare that lights the "
                         "whole temple and anyone standing in it."),
})

# ===========================================================================
# World 4 - The Sunken Coast
# ===========================================================================
KINDS.update({
    'pirate': F('humanoid_rogue', atk_name='Cutlass', die=6,
                skills=['Athletics', 'Stealth'], langs='Common',
                traits_add=['nimble'],
                desc="He has been on this beach a long time and the ship is not "
                     "coming back for him. He wants your boots.",
                tactics="Fights in a crowd, aims for whoever is already hurt, and "
                        "takes to the water when it turns."),
    'crab': F('sea_beast', size='Large', atk_name='Claw', dmg_type='bludgeoning',
              die=8, speed={'walk': 30, 'swim': 30}, ac=3, ac_note='shell',
              traits=['amphib'], guard='shell', rider='grapple',
              desc="Shell like a shield wall and two claws that do not let go. It "
                   "came out of the rock pools for the noise.",
              tactics="Grabs and squeezes. The shell is the real problem."),
    'seagull': F('beast_flyer', size='Medium', type='monstrosity',
                 align='chaotic evil', atk_name='Talons', dmg_type='slashing',
                 die=6, speed={'walk': 20, 'fly': 60}, langs='Common',
                 traits_add=['mimicry', 'keen_sight'],
                 desc="Too big, too loud, and it has your voice off by heart "
                      "already. It calls in the rest with it.",
                 tactics="Shouts in a friend's voice from the cliffs, then dives on "
                         "whoever answers."),
    'captain': F('humanoid_soldier', align='neutral evil',
                 atk_name="Officer's Saber", dmg_type='slashing', die=8,
                 ac=2, ac_note='breastplate', prime='dex', atk_abil='dex',
                 skills=['Athletics', 'Intimidation', 'Perception'], guard='parry',
                 langs='Common', traits_add=['nimble'],
                 desc="He took the Drowned Bell off a church and has not had a quiet "
                      "night since. He will give it back for a price.",
                 tactics="Keeps his crew between you and him, parries the one blow "
                         "that matters, and fights hardest when cornered."),

    'drowned': F('undead_shambler', atk_name='Bloated Fist', die=8,
                 speed={'walk': 20, 'swim': 30}, res_add=['cold'],
                 traits_add=['amphib'], heal='drain',
                 desc="Still in its uniform, still at its post, still full of "
                      "seawater. It went down with the ship and came back up.",
                 tactics="Works below decks where the footing is bad and drags you "
                         "under where it can."),
    'eel': F('sea_beast', size='Medium', atk_name='Bite', die=6,
             speed={'walk': 0, 'swim': 40}, imm=['lightning'],
             traits_add=['light_absorb'], rider='lightning',
             desc="It lives in the flooded hold and the water around it makes your "
                  "teeth ache. Do not stand in the water.",
             tactics="Shocks everything standing in the same water as it."),
    'octopus': F('sea_beast', size='Large', atk_name='Tentacles',
                 dmg_type='bludgeoning', die=8, speed={'walk': 10, 'swim': 60},
                 traits=['amphib'], rider='grapple', guard='coil',
                 desc="Eight arms through the broken hull, each one working on its "
                      "own idea. It only needs two of them on you.",
                 tactics="Grapples two of you at once and pulls them away from the "
                         "rest."),
    'ghostship': F('undead_spirit', size='Large', align='lawful evil',
                   atk_name='Drowning Grasp', dmg_type='cold', die=8,
                   traits_add=['horrify', 'turn_res'], heal='siphon',
                   skills=['Perception'],
                   desc="He went down with the ship because he would not leave the "
                        "wheel, and he is still at it. The wreck follows him around.",
                   tactics="Fills the hold with cold water nobody can see, frightens "
                           "the group apart, and takes them one at a time."),

    'merman': F('humanoid_soldier', size='Medium', align='neutral',
                atk_name='Coral Trident', dmg_type='piercing', die=8,
                speed={'walk': 10, 'swim': 40}, ac=1, ac_note='scale',
                traits_add=['amphib'], langs='Aquan, Common', prime='dex',
                atk_abil='dex',
                desc="He has guarded the reef since long before the bell went into "
                     "it. You are the trespasser here and he is right about that.",
                tactics="Fights from deep water and makes you come to him."),
    'shark': F('sea_beast', size='Large', atk_name='Bite', die=10,
               speed={'walk': 0, 'swim': 60}, traits_add=['blood_frenzy', 'waterbreath'],
               senses=['blindsight 60 ft.'],
               desc="It has been circling since you went in. It gets braver the "
                    "moment anyone starts bleeding.",
               tactics="Waits for the first wound, then will not leave that person "
                       "alone."),
    'siren': F('fey', size='Medium', align='chaotic evil', atk_name='Clawed Hand',
               dmg_type='slashing', die=6, speed={'walk': 20, 'swim': 50},
               traits_add=['amphib', 'fey_charm'], heal='siphon',
               skills_add=['Deception', 'Performance'], langs='Aquan, Common',
               desc="The singing is not for you, it is about you, and it works. The "
                    "reef below her is paved with people who swam toward it.",
               tactics="Charms the strongest swimmer and lets the water finish the "
                       "job."),
    'seaserpent': F('monstrosity', size='Huge', atk_name='Bite', die=12,
                    speed={'walk': 0, 'swim': 60}, ac=2, ac_note='natural armor',
                    traits_add=['waterbreath', 'blood_frenzy'], guard='coil',
                    senses=['blindsight 30 ft.', 'darkvision 60 ft.'],
                    heavy_die=10,
                    desc="Long enough to wrap the reef twice and old enough to have "
                         "seen the temple built. It does not share the water.",
                    tactics="Coils out of reach, then comes in once with everything."),

    'anglerfish': F('sea_beast', size='Large', atk_name='Bite', die=10,
                    speed={'walk': 0, 'swim': 40}, traits_add=['illumination', 'waterbreath'],
                    senses=['blindsight 60 ft.'], heavy_die=10,
                    desc="All you see is the little light. Everything behind the "
                         "light is mouth.",
                    tactics="Hangs still in the black with the lure out and takes "
                            "whoever swims to it."),
    'seawitch': F('humanoid_caster', align='neutral evil', atk_name='Brine Bolt',
                  atk_kind='Ranged Spell Attack', range='60/120 ft.',
                  dmg_type='cold', die=6, speed={'walk': 20, 'swim': 40},
                  traits_add=['amphib'], heal='prayer', langs='Aquan, Common',
                  skills=['Arcana', 'Deception'],
                  desc="She has been trading with drowning sailors for years and has "
                       "never once given a fair price. The temple is hers now.",
                  tactics="Keeps the pillars between you, mends herself, and lets the "
                          "golem hold the floor."),
    'templeguard': F('construct', size='Large', atk_name='Coral Fist', die=10,
                     ac=2, ac_note='natural armor', traits_add=['amphib', 'false_app'],
                     guard='harden', res_add=['bludgeoning, piercing, and slashing '
                                              'from nonmagical attacks'],
                     desc="Grown rather than built, out of live coral and old stone. "
                          "It is part of the temple and the temple is part of it.",
                     tactics="Plants itself in the doorway and hardens. Going around "
                             "it is faster."),
    'kraken': F('monstrosity', size='Gargantuan', align='chaotic evil',
                atk_name='Tentacle', dmg_type='bludgeoning', die=12,
                speed={'walk': 20, 'swim': 60}, ac=3, ac_note='natural armor',
                imm=['lightning'], res_add=['cold'],
                traits_add=['amphib', 'legendary', 'siege'], rider='grapple',
                langs='understands Aquan, Deep Speech and Primordial but cannot speak',
                senses=['truesight 120 ft.'], heavy_die=10,
                desc="It is why the bell was rung, why the bell was sunk, and why "
                     "the coast is empty. It has been under the temple the entire "
                     "time.",
                tactics="Grapples two at once, drags them down, and brings the roof "
                        "in on the rest."),
})
