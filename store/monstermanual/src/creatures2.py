"""Creatures of worlds 5, 6 and 7."""
from families import family as F

KINDS = {}

# ===========================================================================
# World 5 - The Plague Marsh
# ===========================================================================
KINDS.update({
    'plaguerat': F('vermin', size='Small', atk_name='Bite', die=4,
                   speed={'walk': 30, 'swim': 20}, traits=['pack'],
                   imm=['poison'], cond_imm=['poisoned'], rider='poison',
                   desc="It carries the thing that emptied the village and is in no "
                        "danger from it. There are thousands.",
                   tactics="Comes in numbers across the water and bites once each."),
    'leech': F('vermin', size='Medium', atk_name='Bite', die=6,
               speed={'walk': 10, 'swim': 30}, traits=['amphib'],
               heal='feed', rider='grapple', ac=-1,
               desc="Arm-length, boneless, and already attached before you feel it. "
                    "It gets bigger as the fight goes on.",
               tactics="Fastens on and will not let go. Every turn it drinks, it mends."),
    'bogman': F('plant', size='Medium', atk_name='Sodden Fist', die=8,
                speed={'walk': 20, 'swim': 20}, traits_add=['swamp_camo', 'amphib'],
                langs='—', guard='harden', heal='bloom',
                desc="Peat and roots in the shape of a man, standing waist deep where "
                     "it has always stood. It only notices you when you touch the water.",
                tactics="Rises out of the fen behind the group and sets itself. Fire is "
                        "the answer and it knows it."),
    'crocodile': F('sea_beast', size='Huge', atk_name='Bite', die=12,
                   speed={'walk': 30, 'swim': 50}, ac=3, ac_note='natural armor',
                   traits=['hold_breath', 'swamp_camo', 'grappler'],
                   rider='grapple', guard='harden', heavy_die=10,
                   desc="King of the fen by the simple method of eating everything that "
                        "disagreed. He is mostly log until he is not.",
                   tactics="Takes one person in his jaws and rolls. Everything else can "
                           "wait."),

    'plaguedoctor': F('humanoid_caster', align='neutral evil', prime='int',
                      atk_abil='dex', atk_name='Bone Saw',
                      atk_kind='Melee Weapon Attack', dmg_type='slashing', die=6,
                      abil={'int': 5}, save_abil='int', imm=['poison'],
                      cond_imm=['poisoned'], skills=['Medicine', 'Deception'],
                      heal='siphon', rider='poison', langs='Common',
                      desc="He is still making his rounds in a village with nobody left "
                           "in it. He believes he is helping, which is the worst part.",
                      tactics="Insists on treating you. The treatment is the attack."),
    'sickzombie': F('undead_shambler', atk_name='Slam', die=8, imm=['poison'],
                    cond_add=['exhaustion'], rider='poison', traits_add=['stench'],
                    heal='drain',
                    desc="A villager who did not get out in time and did not stay down "
                         "either. The smell arrives first.",
                    tactics="Walks into the middle of you so the stench does the work."),
    'crows': F('swarm_kind', size='Medium', atk_name='Beaks', die=4,
               speed={'walk': 10, 'fly': 50}, traits_add=['keen_sight'],
               desc="They have had a very good month and are not frightened of people "
                    "any more. The whole treeline is black with them.",
               tactics="Lifts off all at once and goes for eyes."),
    'plaguebeast': F('monstrosity', size='Huge', align='chaotic evil', atk_name='Bite',
                     die=12, imm=['poison'], cond_imm=['poisoned'],
                     traits_add=['stench', 'legendary'], rider='poison', heal='feed',
                     heavy_die=10, senses=['darkvision 60 ft.', 'blindsight 30 ft.'],
                     desc="The curse got into something large and made it its own. It is "
                          "the shape of the sickness and the reason it spreads.",
                     tactics="Stands in the open and lets the air around it do half the "
                             "damage, feeding on whoever drops."),

    'frogman': F('monstrosity', size='Medium', atk_name='Tongue',
                 dmg_type='bludgeoning', die=8, speed={'walk': 30, 'swim': 40},
                 traits_add=['amphib', 'standing_leap', 'swamp_camo'],
                 rider='grapple', langs='—',
                 desc="Up on two legs, wider than it is tall, and the tongue comes out "
                      "twenty feet. It eats what it can lift.",
                 tactics="Tongues the lightest of you across the bog and swallows from "
                         "there."),
    'willowisp': F('undead_spirit', size='Tiny', align='chaotic evil', atk_name='Shock',
                   dmg_type='lightning', die=8, speed={'walk': 0, 'fly': 50},
                   imm=['lightning', 'poison'],
                   traits=['incorporeal', 'illumination', 'light_absorb'],
                   heal='siphon', langs='Common',
                   desc="A little light out over the water, exactly where the ground "
                        "stops being ground. It has been doing this a very long time.",
                   tactics="Leads you into the deep bog, puts its light out, and waits."),
    'mosquito': F('beast_flyer', size='Medium', atk_name='Proboscis',
                  dmg_type='piercing', die=4, speed={'walk': 10, 'fly': 50},
                  traits_add=['flyby', 'keen_smell'], heal='feed', rider='poison',
                  desc="Big enough to hear coming, which is the only mercy on offer. It "
                       "drinks and leaves the fever behind.",
                  tactics="Comes in, drinks, and is out of reach before you turn."),
    'bogtroll': F('giant', size='Large', align='chaotic evil', atk_name='Claws',
                  dmg_type='slashing', die=8, speed={'walk': 30, 'swim': 30},
                  senses=['darkvision 60 ft.'],
                  traits_add=['keen_smell', 'amphib', 'swamp_camo', 'stench'],
                  heal='regen', guard='harden', langs='Giant',
                  desc="A troll that has been underwater so long things grow on it. The "
                       "wounds close faster down here.",
                  tactics="Fights from the water where the footing is yours to lose, and "
                          "heals between every exchange."),

    'hagspawn': F('fey', size='Medium', align='neutral evil', atk_name='Claws',
                  atk_kind='Melee Weapon Attack', dmg_type='slashing', die=6,
                  prime='dex', atk_abil='dex', speed={'walk': 30, 'swim': 30},
                  traits_add=['amphib', 'swamp_camo'], heal='siphon',
                  langs='Sylvan, Common',
                  desc="The hag has children and this is one of them. It has her temper "
                       "and none of her patience.",
                  tactics="Fights in a pair with its sibling and screams for mother when "
                          "it is losing."),
    'rootbeast': F('plant', size='Large', atk_name='Root Lash', die=8,
                   traits_add=['false_app', 'swamp_camo'], guard='harden',
                   heal='bloom', rider='grapple',
                   desc="The lair has roots that reach further than the tree they came "
                        "from. They take hold of ankles.",
                   tactics="Looks exactly like the floor until someone stands on it."),
    'slime': F('ooze', size='Large', atk_name='Pseudopod', dmg_type='poison', die=8,
               traits_add=['ooze_amorph'], heal='mend', rider='poison',
               desc="Green, thigh-deep, and working its way slowly across the lair "
                    "floor. It dissolves what it covers.",
               tactics="Oozes onto whoever stands still and splits when you cut it."),
    'boghag': F('fey', size='Medium', align='neutral evil', prime='cha', atk_abil='cha',
                atk_name="Hag's Claws", atk_kind='Melee Weapon Attack',
                dmg_type='slashing', die=8, speed={'walk': 30, 'swim': 30},
                ac=2, ac_note='natural armor',
                traits_add=['amphib', 'magic_res', 'legendary', 'shapechanger'],
                heal='siphon', skills_add=['Deception', 'Insight'],
                langs='Common, Sylvan',
                desc="She put the rot on the marsh and she can take it off, for a price "
                     "that is always a person. She will look like someone you trust when "
                     "you come in.",
                tactics="Wears a friendly face until the door shuts, then fights with "
                        "everything and keeps mending."),
})

# ===========================================================================
# World 6 - The Iron Mines
# ===========================================================================
KINDS.update({
    'kobold': F('humanoid_rogue', size='Small', tag='kobold', atk_name='Pick',
                dmg_type='piercing', die=6, langs='Common, Draconic',
                senses=['darkvision 60 ft.'], traits_add=['pack', 'sunlight'],
                desc="It has worked this shaft its whole life and knows every prop that "
                     "will not hold. That is the whole plan.",
                tactics="Fights where the roof is weak and pulls it down on you."),
    'caveworm': F('monstrosity', size='Large', atk_name='Bite', die=10,
                  speed={'walk': 20, 'burrow': 30},
                  senses=['blindsight 60 ft.', 'tremorsense 60 ft.'],
                  traits_add=['tunneler', 'earth_glide'], langs='—',
                  desc="It eats the rock and does not much mind what is in the rock. The "
                       "tunnels down here are all its work.",
                  tactics="Comes out of a wall nobody was watching."),
    'minebat': F('swarm_kind', size='Medium', atk_name='Bites', die=4,
                 speed={'walk': 5, 'fly': 60}, senses=['blindsight 60 ft.'],
                 traits_add=['echo'],
                 desc="The whole roof of the shaft moves when the lantern goes near it. "
                      "Then it comes down.",
                 tactics="Fills the tunnel and puts out your light."),
    'foreman': F('humanoid_soldier', size='Small', tag='goblinoid', align='lawful evil',
                 atk_name='Iron Lash', dmg_type='slashing', die=8, ac=2,
                 ac_note='scavenged plate', langs='Common, Goblin',
                 senses=['darkvision 60 ft.'], skills_add=['Intimidation'],
                 guard='shield',
                 desc="He runs the shift and the shift runs scared. He has the keys to "
                      "the Great Forge on a chain round his neck.",
                 tactics="Keeps the miners swinging and stays behind them until there is "
                         "nobody left to stay behind."),

    'crystalgolem': F('construct', size='Large', atk_name='Crystal Fist', die=8, ac=2,
                      ac_note='natural armor', res_add=['radiant'],
                      traits_add=['stone_camo'], guard='harden', heal='mend',
                      desc="Grown out of the cavern wall and shaped like something that "
                           "walks. It rings when you hit it and that is about all.",
                      tactics="Sets itself in the narrow part of the cavern and waits for "
                              "you to tire."),
    'basilisk': F('monstrosity', size='Medium', atk_name='Bite', die=10,
                  speed={'walk': 20}, ac=3, ac_note='natural armor',
                  senses=['darkvision 60 ft.'], guard='harden',
                  desc="Eight legs, bad breath, and a look that turns people into part of "
                       "the scenery. Half the statues down here were walking last year.",
                  tactics="Meets your eye on purpose. Fight it looking at the floor."),
    'gemspider': F('vermin', size='Medium', atk_name='Bite', dmg_type='piercing', die=6,
                   speed={'walk': 30, 'climb': 30}, res_add=['radiant'],
                   senses=['darkvision 60 ft.'],
                   traits_add=['webwalker', 'stone_camo'], rider='poison',
                   ac=2, ac_note='crystal carapace',
                   desc="Its back is set with stones worth more than the mine. That is "
                        "why people come down here, and why they stop.",
                   tactics="Hangs in the crystal where it cannot be told apart from it."),
    'crystaldrake': F('dragonkin', size='Large', atk_name='Bite', die=10, ac=3,
                      ac_note='crystal hide', res_add=['radiant', 'piercing'],
                      heavy_die=8, breath='force', traits_add=['stone_camo'],
                      desc="Grown in the cavern and made of the same stuff as the walls. "
                           "Its breath comes out as a sheet of splinters.",
                      tactics="Shatters the crystal around you, then picks off whoever is "
                              "bleeding."),

    'magmaslime': F('ooze', size='Large', atk_name='Pseudopod', dmg_type='fire', die=8,
                    imm=['fire', 'poison'], speed={'walk': 20, 'climb': 20},
                    traits_add=['fire_absorb', 'aura_fire', 'illumination'],
                    heal='ember',
                    desc="It comes up through the floor of the tunnel and goes where it "
                         "likes. Everything it has crossed is still burning.",
                    tactics="Rolls onto you so standing next to it costs you every turn."),
    'salamander': F('elemental', size='Medium', align='neutral evil', atk_name='Bite',
                    atk_kind='Melee Weapon Attack', dmg_type='fire', die=8,
                    speed={'walk': 30, 'climb': 30}, prime='str', atk_abil='str',
                    imm=['fire', 'poison'], vuln=['cold'], res=[],
                    traits=['aura_fire', 'fire_absorb'], langs='Ignan', heal='ember',
                    cond_imm=['exhaustion', 'poisoned'],
                    desc="It lives in the lava the way a fish lives in a river and comes "
                         "out for company. Touching it is a mistake.",
                    tactics="Closes in and stays close. Cold is the quick way."),
    'firedwarf': F('humanoid_soldier', align='chaotic evil', tag='dwarf',
                   atk_name='Forge Hammer', dmg_type='bludgeoning', die=8, ac=2,
                   ac_note='scorched mail', res_add=['fire'],
                   senses=['darkvision 60 ft.'], langs='Common, Dwarvish',
                   guard='parry', heal='ember', skills_add=['Athletics'],
                   desc="He was a smith down here before the forge was taken, and "
                        "something in the heat got into him. He still thinks he is at "
                        "work.",
                   tactics="Hammers whoever is nearest and does not register that he is "
                           "losing."),
    'lavagolem': F('construct', size='Large', atk_name='Molten Fist', dmg_type='fire',
                   die=10, ac=1, ac_note='natural armor',
                   imm=['fire', 'poison', 'psychic'], vuln=['cold'],
                   traits_add=['aura_fire', 'fire_absorb', 'illumination'],
                   heal='ember', heavy_die=8,
                   desc="Someone poured the forge into a mold and it got up. It leaves "
                        "its own footprints burned into the rock.",
                   tactics="Walks into the middle of the party and stands there glowing."),

    'clockwork': F('construct', size='Medium', atk_name='Blade Arm',
                   dmg_type='slashing', die=8, ac=3, ac_note='iron plating',
                   speed={'walk': 30}, guard='parry', heal='mend',
                   desc="Wound up a hundred years ago and still at its post. It does not "
                        "tire, bleed, or ask who you are.",
                   tactics="Fights exactly the same way every round, which is its one "
                           "weakness."),
    'forgehound': F('construct', size='Medium', atk_name='Bite', dmg_type='fire',
                    die=8, speed={'walk': 50}, imm=['fire', 'poison', 'psychic'],
                    traits_add=['pack', 'aura_fire', 'keen_smell'], heal='ember',
                    desc="Built to keep thieves out of the Great Forge and never told the "
                         "forge had been stolen. Red hot all the way through.",
                    tactics="Runs down whoever tries to leave the forge floor."),
    'smithimp': F('fiend', size='Small', atk_name='Hot Tongs', dmg_type='fire', die=6,
                  speed={'walk': 30, 'fly': 40}, traits_add=['flyby', 'aura_fire'],
                  heal='ember', langs='Infernal, Common',
                  desc="It works the bellows and enjoys it far too much. It throws what "
                       "is in the fire at you.",
                  tactics="Stays by the furnace, pelts you with whatever is glowing, and "
                          "never lands."),
    'irongolem': F('construct', size='Huge', atk_name='Iron Fist', die=12, ac=4,
                   ac_note='iron plating',
                   imm=['fire', 'poison', 'psychic',
                        'bludgeoning, piercing, and slashing from nonmagical attacks '
                        "that aren't adamantine"],
                   traits_add=['immutable', 'legendary', 'siege', 'magic_weapons'],
                   heavy_die=10, heal='mend',
                   desc="The Great Forge did not make it. The Great Forge is inside it. "
                        "Whoever ordered that has not been seen since.",
                   tactics="Takes the whole party's best round without flinching, and "
                           "then begins."),
})

# ===========================================================================
# World 7 - The Haunted Abbey
# ===========================================================================
KINDS.update({
    'gravedigger': F('undead_shambler', atk_name='Spade', dmg_type='slashing', die=8,
                     speed={'walk': 25}, traits_add=['undead_fort'], heal='mend',
                     desc="He dug every grave in this yard, including the last one, and "
                          "he is still working. He does not like the holes standing "
                          "empty.",
                     tactics="Swings the spade and keeps backing toward the open grave he "
                             "wants you in."),
    'ghoulhound': F('undead_shambler', align='chaotic evil', atk_name='Bite',
                    dmg_type='piercing', die=8, speed={'walk': 50},
                    traits_add=['pack', 'keen_smell'], heal='feed',
                    cond_add=['charmed'],
                    desc="Something that was a dog, kept on well past the point it should "
                         "have been let go. It smells graves from a mile out.",
                    tactics="Runs in a pack and brings people down to be fed on."),
    'banshee': F('undead_spirit', size='Medium', atk_name='Wailing Touch',
                 dmg_type='necrotic', die=8, traits_add=['horrify'], heal='siphon',
                 langs='Common, Elvish',
                 desc="She died in the abbey the night the bells stopped and has been "
                      "telling everyone about it since. The scream is the dangerous part.",
                 tactics="Screams once at the whole group, then drains whoever stayed."),
    'headless': F('undead_knight', align='lawful evil', atk_name='Greatsword',
                  dmg_type='slashing', die=10, ac=3, ac_note='plate',
                  traits_add=['magic_weapons', 'relentless'], heal='drain',
                  skills=['Athletics'], senses=['blindsight 60 ft.'],
                  desc="He is looking for his head and is reasonably sure one of yours "
                       "will do. He does not need eyes to find you.",
                  tactics="Guards against the first blow, then swings twice and once more "
                          "harder."),

    'ghostmonk': F('undead_spirit', align='neutral', atk_name='Ascetic Strike',
                   atk_kind='Melee Spell Attack', dmg_type='force', die=8,
                   traits_add=['magic_res'], heal='prayer',
                   skills_add=['Religion', 'Insight'], langs='Common',
                   desc="He kept the hours before and keeps them now, and you are "
                        "standing in the cloister during prayers. He would rather you "
                        "left.",
                   tactics="Fights only as long as you are in the cloister. Mends himself "
                           "and the others first."),
    'gargoylepup': F('construct', size='Small', type='elemental', align='chaotic evil',
                     atk_name='Claws', dmg_type='slashing', die=6,
                     speed={'walk': 30, 'fly': 50},
                     res=['bludgeoning, piercing, and slashing from nonmagical attacks '
                          "that aren't adamantine"],
                     imm=['poison'], cond_imm=['exhaustion', 'petrified', 'poisoned'],
                     traits=['false_app'], langs='Terran', guard='harden', heal='mend',
                     desc="Half the size of the ones on the roof and twice as quick. There "
                          "are a great many of them along the cloister wall.",
                     tactics="Sits in the stonework in a row, and all of them come off at "
                             "once."),
    'poltergeist': F('undead_spirit', size='Tiny', atk_name='Hurled Object',
                     atk_kind='Ranged Spell Attack', range='60 ft.',
                     dmg_type='bludgeoning', die=6, traits_add=['incorporeal'],
                     heal='siphon', langs='—',
                     desc="You cannot see it and it can lift a pew. Everything in the "
                          "cloister is its weapon.",
                     tactics="Throws the furniture from across the room and never comes "
                             "close."),
    'abbot': F('undead_knight', align='lawful evil', prime='wis', atk_abil='wis',
               atk_name='Crozier', atk_kind='Melee Spell Attack', dmg_type='necrotic',
               die=8, ac=1, ac_note='vestments', abil={'wis': 5}, save_abil='wis',
               traits_add=['magic_res', 'legendary', 'turn_imm'], heal='prayer',
               skills=['Religion', 'Persuasion', 'Insight'], langs='Common',
               desc="He silenced the bells himself and has a long explanation ready. He is "
                    "sure the abbey is better this way.",
               tactics="Keeps his congregation standing, mends constantly, and will not be "
                       "turned."),

    'bonewalker': F('undead_shambler', atk_name='Bone Club', die=8,
                    vuln=['bludgeoning'], cond_add=['exhaustion'],
                    traits_add=['undead_fort'], guard='harden', heal='mend',
                    desc="Built out of whatever the catacombs had spare, which was a lot. "
                         "It has more arms than it strictly needs.",
                    tactics="Sets itself in the narrow passage so only one of you can "
                            "reach it."),
    'cryptrat': F('swarm_kind', size='Large', atk_name='Bites', die=4,
                  speed={'walk': 30, 'climb': 20}, traits_add=['keen_smell'],
                  rider='poison',
                  desc="One rat the size of a hound and several hundred that are not. The "
                       "big one decides where they all go.",
                  tactics="Pours along the bone shelves and drops on you from both sides."),
    'wight': F('undead_knight', align='neutral evil', atk_name='Barrow Blade',
               dmg_type='slashing', die=8, ac=2, ac_note='ancient mail',
               traits_add=['sunlight', 'turn_res'], heal='drain',
               skills=['Perception', 'Stealth'],
               desc="Buried with his sword and his rings, and he still has strong feelings "
                    "about both. Anyone he kills gets up again on his side.",
               tactics="Drains the toughest of you to raise them, and avoids the stairs up "
                       "to daylight."),
    'bonedragon': F('dragonkin', size='Huge', type='undead', atk_name='Bite', die=12,
                    ac=2, ac_note='bare bone', imm=['poison', 'necrotic'],
                    cond_imm=['exhaustion', 'poisoned', 'charmed', 'frightened'],
                    vuln=['bludgeoning'], heavy_die=8, breath='necrotic',
                    traits_add=['legendary', 'turn_res', 'magic_weapons'],
                    langs='understands Draconic but cannot speak',
                    desc="The abbey was built on top of it, and the catacombs are just the "
                         "parts of it they dug around. There is no flesh left and no less "
                         "of it.",
                    tactics="Fills the catacomb with grave air, then bites twice from the "
                            "dark."),

    'darkpriest': F('humanoid_caster', align='neutral evil', prime='wis',
                    atk_abil='wis', atk_name='Shadow Bolt',
                    atk_kind='Ranged Spell Attack', range='60/120 ft.',
                    dmg_type='necrotic', die=6, abil={'wis': 4}, save_abil='wis',
                    skills=['Religion', 'Deception'], heal='prayer',
                    res_add=['necrotic'],
                    desc="He serves the thing in the bell tower and runs its errands "
                         "gladly. There is nothing left to bargain with.",
                    tactics="Hides behind the knight, keeps it upright, and throws the dark "
                            "at whoever gets past."),
    'vampirebat': F('beast_flyer', size='Medium', atk_name='Bite', dmg_type='piercing',
                    die=6, speed={'walk': 5, 'fly': 60},
                    senses=['blindsight 60 ft.'], traits_add=['echo', 'flyby'],
                    heal='feed',
                    desc="It roosts in the bell and drinks what the tower leaves it. "
                         "Dog-sized, and it has had plenty.",
                    tactics="Dives, drinks, and climbs out of reach to swallow."),
    'deathknight': F('undead_knight', align='lawful evil', atk_name='Black Blade',
                     dmg_type='slashing', die=10, ac=4, ac_note='plate, shield',
                     traits_add=['magic_weapons', 'magic_res', 'turn_res'],
                     guard='shield', heal='drain',
                     skills=['Athletics', 'Perception'],
                     desc="The best of the abbey's guard, kept on past death and fully "
                          "aware of it. He is not sorry.",
                     tactics="Shields the first attack, then two blows and a third that "
                             "drains."),
    'lich': F('undead_knight', size='Medium', align='neutral evil', prime='int',
              atk_abil='int', atk_name='Paralyzing Touch',
              atk_kind='Melee Spell Attack', dmg_type='cold', die=8, ac=2,
              ac_note='warding', abil={'int': 6}, save_abil='int',
              imm=['poison', 'necrotic'],
              res=['cold', 'lightning',
                   'bludgeoning, piercing, and slashing from nonmagical attacks'],
              cond_imm=['charmed', 'exhaustion', 'frightened', 'paralyzed', 'poisoned'],
              traits_add=['magic_res', 'legendary', 'rejuvenate', 'turn_res'],
              heal='siphon', skills=['Arcana', 'History', 'Insight', 'Perception'],
              langs='Common and four other languages', heavy_die=8,
              desc="It stopped the bells because the bells were the one thing that could "
                   "reach it. Everything else in the abbey is its work.",
              tactics="Never comes within reach if it can help it, and comes back in a "
                      "week if you leave its anchor in the tower."),
})
