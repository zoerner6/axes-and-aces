"""All the written content of the book."""

TITLE = 'The Axes & Aces Monster Manual'
SUBTITLE = '168 monsters from the ten worlds'
TAGLINE = 'Fifth Edition compatible'
SITE = 'AxesAndAces.com'

# The attribution statement below is reproduced exactly as the System
# Reference Document 5.1 requires it. Do not reword it, and do not add any
# other mention of the rights holder anywhere in the book.
SRD_NOTICE = (
    'This work includes material taken from the System Reference Document 5.1 '
    '("SRD 5.1") by Wizards of the Coast LLC and available at '
    'https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 '
    'is licensed under the Creative Commons Attribution 4.0 International '
    'License available at https://creativecommons.org/licenses/by/4.0/legalcode.'
)

SRD_MODIFICATIONS = (
    'Modifications: this book is a new work built on SRD 5.1. Creature trait '
    'and action wording is taken from SRD 5.1 and adapted to each creature by '
    'substituting its name and its own numbers. Every stat block, challenge '
    'rating, description and piece of fiction in this book is new material and '
    'is not part of SRD 5.1.'
)

AI_DISCLOSURE_TITLE = 'How this book was made'

AI_DISCLOSURE = (
    'Every illustration in this book was generated with an AI image model. '
    'The text was written with AI assistance. Nothing here was drawn or '
    'written by a human artist or author working by hand.\n\n'
    'The pictures come straight out of the Axes & Aces card game, where they '
    'have been in use since the game launched. They were made with Google\'s '
    'Gemini image model, the one commonly called nano-banana. The creature '
    'names, the ten worlds, the areas and the balance numbers behind every '
    'stat block are the game\'s own data, not invented for this book.\n\n'
    'If AI art or AI writing is not something you want to pay for, do not buy '
    'this book. That is a fair position and this page is here so you can take '
    'it before you spend anything rather than after.'
)

COPYRIGHT = (
    'Axes & Aces, the Axes & Aces logo, the ten worlds and the creature names '
    'in this book are the property of the publisher. The game is free to play '
    'at ' + SITE + '.'
)

# ---------------------------------------------------------------------------
# Introduction
# ---------------------------------------------------------------------------
INTRO = [
    ('What this is',
     "This is a bestiary of 168 monsters, drawn from the card game Axes & "
     "Aces. The game has ten worlds in it, and you fight your way through each "
     "one with poker hands. Every monster in it has a picture, a home, and a "
     "set of numbers. This book takes all three and turns them into stat "
     "blocks you can put on a table.\n\n"
     "It is a book of monsters and nothing else. There is no setting to buy "
     "into, no new rules to learn, and no adventure you have to run. Drop any "
     "creature in this book into whatever game you are already running."),

    ('How the book is laid out',
     "The monsters are grouped by the ten worlds of the game rather than "
     "alphabetically, because the worlds run from easiest to hardest. World "
     "one is a tavern cellar. World ten is the Abyss. If you read the book "
     "front to back you are walking the same road the game walks, and the "
     "challenge ratings climb with you.\n\n"
     "Each world has four areas, and each area has its monsters and one boss. "
     "Bosses get a page of their own. If you want a monster by name or by "
     "challenge rating instead, there are tables for both at the back."),

    ('Where the numbers come from',
     "The game is balanced for poker hands, not for four people around a "
     "table, so none of its numbers are copied across raw. Every stat block "
     "here was worked out from the game's own data by one method, applied the "
     "same way to all 168 creatures. It runs like this.\n\n"
     "FIRST, WHERE IT LIVES GIVES ITS LEVEL. The game has forty areas: ten "
     "worlds of four. Spread those evenly over character levels 1 to 20 and "
     "each area lands on a party level, two areas to a level. A monster from "
     "the first area of world one is written for a 1st-level party. A monster "
     "from the last area of world ten is written for a 20th-level party.\n\n"
     "SECOND, RANK AND FILE COME IN GROUPS. In the game you meet ordinary "
     "monsters several at a time, so one of them is worth about half a party "
     "level. Its own health and attack multipliers scale that up or down: a "
     "monster carrying one and a half times the usual health lands higher than "
     "one carrying three quarters of it. A boss is fought alone, so a boss "
     "sits two ratings above its party level.\n\n"
     "THIRD, SHELL OR TEETH DECIDES WHERE THE RATING GOES. The game reads "
     "every monster's health against its attack to work out whether it is "
     "mostly armor or mostly bite, and the same reading is used here. A "
     "shelled monster spends its rating on armor class and hit points and hits "
     "softly. A fast one has worse armor and hits hard. The rating is the same "
     "either way, which is why a Stone Gargoyle and a Castle Ghost can sit at "
     "the same number and feel nothing alike.\n\n"
     "FOURTH, ITS ATTACK PATTERN GIVES IT ITS ACTIONS. Every monster in the "
     "game has a short pattern it repeats. Numbers in the pattern are swings, "
     "so a monster with three of them gets a multiattack and one with a single "
     "swing does not. A pattern that ends on a much larger number gets a heavy "
     "blow that recharges. A turn the monster spends blocking becomes a parry, "
     "a shield wall or a bonus action to set itself. A turn it spends healing "
     "becomes regeneration, a life drain, or a bonus action to mend.\n\n"
     "The ordinary attacks deliberately carry well under half of what the "
     "rating allows, with the recharging blow making up the rest. That is how "
     "published creatures are built, and matching it is what keeps these "
     "blocks feeling like the real thing instead of arithmetic."),

    ('What this means for you at the table',
     "A boss sits two ratings above its party level, which at low levels is a "
     "genuinely deadly fight for four characters. That is the point of a boss, "
     "but go in knowing it. If you want it survivable, send the area's "
     "ordinary monsters in first and let the party spend resources on them, or "
     "run the boss with half its hit points and keep everything else.\n\n"
     "The challenge ratings here were derived by formula, not playtested "
     "against a hundred tables. They are consistent with each other, which is "
     "the thing that matters most when you are picking a monster: if one "
     "creature in this book is a harder fight than another, the number says "
     "so. Treat them the way you would treat any rating, as a starting point "
     "you adjust for your own group."),

    ('Bosses and their one trick',
     "In the card game every boss ignores one suit. Play a heart against a "
     "boss that is immune to hearts and nothing happens at all. A quarter of "
     "your hand stops working and you have to fight differently.\n\n"
     "That rule is carried over here as resistance to one damage type the "
     "party is almost certainly using. Spades became slashing, clubs became "
     "bludgeoning, diamonds became piercing, and hearts became psychic damage "
     "plus immunity to being charmed. It asks the same question of the party "
     "that the card game asks of the player: what else have you got?"),

    ('Variants, and getting more than 168 monsters out of this',
     "The card game fills out its areas by recoloring a monster and giving it "
     "a new name, so a Sneaky Goblin also turns up as a Frost Goblin and an "
     "Ember Goblin. Those are not in this book, because a recolored picture and "
     "a new name is not a monster worth a page.\n\n"
     "The trick is worth having, though, and it works at a table. Take any "
     "creature in this book, swap its damage type, and give it a matching "
     "name. A frost version carries a fifth more hit points and hits a fifth "
     "softer. An ember version is the other way round. A shadow version swaps "
     "its damage for necrotic and gains resistance to it. None of that changes "
     "the challenge rating enough to matter, and it gets you three or four "
     "monsters out of every entry."),

    ('Reading an entry',
     "Each entry gives the creature's picture, its size and kind, its armor "
     "class and hit points, its speeds, its six ability scores, whatever it "
     "resists or ignores, its traits, and its actions. Underneath that are two "
     "lines that are not rules: what the creature is, and how it fights. The "
     "second one is the useful one. Read it before you run the monster and you "
     "will know what it should be doing on its turn.\n\n"
     "Above the stat block you will also find the party level the creature was "
     "written for, and the world and area it comes from in the game. The "
     "numbers in brackets after the rating are the game's own health and attack "
     "multipliers, left in so you can see the working."),
]

# ---------------------------------------------------------------------------
# One short in-world piece per world. Bram keeps the tavern and has been
# further than he lets on.
# ---------------------------------------------------------------------------
BRAM = {
    'w1': ("Everybody starts here. Nobody plans to.\n\n"
           "The Gilded Ace is a public house with a cellar under it and a wood "
           "behind it, and that is all it was for thirty years. Then they took "
           "Anna down the cellar stairs and the whole thing turned out to be "
           "the first mile of something much longer. Keep that in mind when you "
           "send a party into a tavern. The monsters in this world are small. "
           "The road out of it is not."),

    'w2': ("Cold kills more people up there than the monsters do, and the "
           "monsters know it.\n\n"
           "Nothing in the Frozen Peaks needs to beat you. It only needs to "
           "keep you out in the open until the weather has you. Every creature "
           "in this world fights like it has all day, because it does. If you "
           "run these monsters and your party is winning comfortably, you have "
           "forgotten to make the cold cost them something."),

    'w3': ("The caravan did not get lost. I want that understood.\n\n"
           "Thirty people and eleven wagons on a road they had all walked "
           "before, and not one track leading off it. The desert does not "
           "mislay things. Something in it took them, all at once, in one "
           "place. The monsters in the Burning Sands are mostly patient, mostly "
           "buried, and mostly bigger than what you came prepared for."),

    'w4': ("They sank the bell on purpose. Think about why.\n\n"
           "A church bell is heavy, it is expensive, and it is the loudest "
           "thing a village owns. You do not drop one in the sea because you "
           "are tired of ringing it. You drop it there because something came "
           "when it rang and you could not think of anything else to try. "
           "Everything in the Sunken Coast is downstream of that decision."),

    'w5': ("You will want to burn it. Everyone wants to burn it.\n\n"
           "The Plague Marsh does not catch, that is the trouble, and the "
           "things living in it have had a long time to get used to people "
           "arriving with torches. Half of what is in this world heals faster "
           "than you can hurt it and the other half does not need to beat you "
           "at all, only breathe on you. Go in clean, come out quick, and do "
           "not drink anything."),

    'w6': ("A forge is not a thing that can be stolen. And yet.\n\n"
           "The Iron Mines were the best-run works in the kingdom and now the "
           "shifts go down and do not come back up, and whatever is making "
           "things down there is making them out of the miners' own tools. "
           "There is a great deal of stone and fire between you and the "
           "bottom. The monsters in this world are mostly made rather than "
           "born, which means somebody is making them."),

    'w7': ("Bells are a warning. Silence is the news.\n\n"
           "The abbey rang the hours for four hundred years and you could set "
           "your day by it from the valley floor. Then it stopped, and nobody "
           "has gone up to ask why, and the people who did go up are part of "
           "what is in this world now. Nothing in the Haunted Abbey stays "
           "dead, so stop trying to make it. Work out what is holding it here "
           "instead."),

    'w8': ("The elves were not the problem. That is the part people get wrong.\n\n"
           "Something got into the wood and into the heart tree and then into "
           "them, and they were the last line against it before they were the "
           "thing itself. Every creature in the Elven Wilds was something "
           "better once and most of them still move beautifully. It does not "
           "help you. The thorn is the monster and everything else in this "
           "world is just where it got to."),

    'w9': ("You cannot flank a thing that is standing on the sky.\n\n"
           "The Sky Fortress is a bad place to fight and it was built to be "
           "one. Narrow bridges, long drops, and everything that lives up there "
           "flies. Half the monsters in this world will not kill your party at "
           "all; they will put them over the edge and let the ground finish it. "
           "Run them that way. The fall is the monster."),

    'w10': ("I have not been. I will not pretend otherwise.\n\n"
            "Everything in this last world was already working for the thing on "
            "the throne before anyone went looking for it, including a fair "
            "amount of what you fought in the other nine. These are the hardest "
            "creatures in the book and they are meant to be the end of "
            "something. If your party reaches the Abyss, let it cost them. "
            "There is no eleventh world to save anything for."),
}

APPENDIX_CR = (
    'Every creature in the book by challenge rating, for when you know how '
    'hard a fight you want and do not mind what shows up.'
)

APPENDIX_AZ = 'Every creature in the book by name.'

STORE_BLURB_HEAD = 'A bestiary of 168 monsters, in ten worlds, from a free card game.'

# The back of the printed book. Kept short: it has to read at arm's length
# in a thumbnail as well as in the hand.
BACK_COVER = (
    "Every monster from the card game Axes & Aces, with a full stat block "
    "and a picture, ready to drop on a table.\n\n"
    "Ten worlds, easiest to hardest. A tavern cellar, frozen peaks, burning "
    "sands, a sunken coast, a plague marsh, iron mines, a haunted abbey, "
    "elven wilds, a sky fortress, and the Abyss. World one is written for a "
    "1st-level party. World ten is written for a 20th.\n\n"
    "Forty of them are bosses, each on a page of its own, each with the one "
    "trick that makes it different.\n\n"
    "No setting to buy into and no new rules to learn. The introduction "
    "shows exactly how the card game's numbers became challenge ratings, so "
    "you can see the working and decide whether to trust it.\n\n"
    "168 monsters. Challenge 1/2 to 22."
)
