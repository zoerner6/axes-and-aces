# Audit of the Monster Manual, 2 November 2026

> **A correction to finding A1, written while fixing it.** The first version
> of this audit measured every creature against the Dungeon Master's Guide's
> Monster Statistics by Challenge Rating table and reported a mean error of
> +1.78. That number is right at mid and high ratings and overstated at the
> bottom, because the DMG's low hit point rows do not describe published
> creatures either: the table asks for 50-70 hit points at challenge 1/2,
> where the SRD's own orc has 15, its black bear 19 and its worg 26. Taking
> the table literally produced a 67-point zombie. The finding stands —
> the top of the book really was wearing ratings it had not earned — but the
> remedy had to follow published creatures at the bottom and the table at the
> top. See **What was done** at the end.

Everything below was measured against the built PDF and `build/blocks.json`,
not guessed. Counts are exact.

The book is complete, honest and well laid out. Contents page numbers are
correct, all 168 monsters have art, no page overflows, no missing glyphs,
every stat block has a name, size, type, alignment, AC, HP, speed, six
ability scores, languages, challenge rating and XP.

What follows is what is wrong with it and what a DM would reach for and not
find.

---

## A. Things that are wrong

### A1. The challenge ratings are inflated, badly, and worst at the top

This is the serious one. Measured every creature against the DMG's own
Monster Statistics by Challenge Rating table — defensive CR from hit points
and armor class, offensive CR from damage per round and attack bonus, final
CR the average of the two.

**76 of 168 creatures sit 2 or more challenge ratings away from the number
printed on them. The mean error is +1.78 — the book says harder than it is.**

The error is small at the bottom and large at the top:

| Creature | Printed | Derived | HP | AC | DPR | Attack |
|---|---|---|---|---|---|---|
| The Flame Fiend | 22 | 18.5 | 333 | 20 | 101.5 | +14 |
| Cerberus | 21 | 17.5 | 315 | 20 | 98.2 | +13 |
| The Pit Warden | 21 | 17.5 | 310 | 21 | 98.2 | +13 |
| The Storm Titan | 20 | 16.5 | 294 | 21 | 92.5 | +13 |
| The Thorn Queen | 18 | 14.5 | 272 | 20 | 80.3 | +12 |
| The Dark Unicorn | 17 | 13.2 | 256 | 17 | 78.9 | +12 |
| The Lich | 16 | 12.5 | 246 | 18 | 73.7 | +11 |
| The Bog Troll | 12 | 8.5 | 187 | 16 | 55.8 | +9 |

The DMG wants 446–490 hit points and 159–176 damage a round at CR 22. The
Flame Fiend has 333 and 101. It is a CR 18 monster wearing a CR 22 label.

Low-level creatures are close to right: the Dark Knight, Tavern Bat, Giant
Spider and friends all land within half a rating.

Why this matters more than it looks: CR is not decoration. A DM builds an
encounter by spending an XP budget, and the XP comes from the CR. A party
told to expect a deadly fight against a CR 22 demon gets a medium one. The
introduction says the ratings are "consistent with each other", and they are
— but they are consistently wrong against the standard every other 5E book
is built to, which is the one a DM is actually using.

### A2. Not one creature has a saving throw proficiency

All 168 have an empty saves list. In the SRD, most creatures above about CR 5
have two or three, and legendary creatures always do.

This compounds A1. A CR 22 demon with no Wisdom save proficiency and no
Constitution save proficiency fails almost everything a 20th-level party
throws at it. It gets banished, dominated, stunned or polymorphed on round
one. Legendary Resistance 3/day covers three of those and then it is over.

### A3. Thirteen creatures print their skills twice

The Storm Giant's line reads `Skills Athletics +13, Perception +12, Athletics
+13, Perception +12`. Affected: Grimstone Dragon, The Frost Giant, Bone
Vulture, Cursed Dwarf, Wicked Pixie, The Thorn General, The Thorn Queen,
Storm Harpy, and five more. A `skills_add` list is being concatenated onto a
family default that already contains the same entries.

### A4. Six attacks give damage with no dice

Every other attack in the book reads `Hit: 4 (1d6 + 1) bludgeoning damage`.
The six Life Drain attacks read `Hit: 2 necrotic damage` — a flat number, no
dice. 168 attacks with dice, 6 without, and the 6 are exactly the
self-healing ones. The `drain` entry in `families.py` writes `{x}` directly
instead of going through the same dice helper as everything else.

### A5. The Sky Serpent is a dragon with no breath weapon

Five of the six dragons have one. The Sky Serpent does not.

### A6. Six of eight elementals have no darkvision

The Dark Djinn, Fire Spirit, Fire Salamander, Wind Spirit, Air Elemental and
Cloud Djinn all have an empty senses line. Every elemental in the SRD has
darkvision 60 ft. The two that do have it are the gargoyles.

Undead and fiends are all correct — this is confined to elementals.

---

## B. Things missing from the stat blocks

### B1. No legendary actions, on any of the forty bosses

They have Legendary Resistance. They have no legendary actions.

Twenty-six of the forty bosses are CR 10 or higher and the ladder tops out at
CR 22. These are written to be fought alone — the introduction says so. A
solo monster with one turn against four or five characters loses on action
economy before its hit points matter: the party acts five times for every
once it does. Legendary actions are the mechanism 5E uses to fix exactly
this, and every published solo boss has them.

Of all the gaps in this book, this is the one that changes how the fights
actually go.

### B2. No lair actions or regional effects

The ten world bosses — Grimstone Dragon, The Frost Giant, The Scorched King,
The Kraken, The Bog Hag, The Iron Golem, The Lich, The Thorn Queen, The Storm
Titan, The Demon King — are each the climax of a world with a named,
described place. That is exactly the setup lair actions exist for, and the
book has the locations written already.

### B3. Not one creature can cast a spell

Nine creatures are named and described as spellcasters and all nine swing a
weapon instead:

Swamp Witch (CR 1), Frost Shaman (CR 2), Cult Priest (CR 3), Sea Witch
(CR 4), The Ice Witch (CR 5), Shadow Priest (CR 8), Thorn Mage (CR 9),
Demon Sorcerer (CR 13), The Lich (CR 16).

A lich that cannot cast a spell is the detail that tells a reader the book
was generated rather than written.

### B4. Sixteen creatures have no traits at all

Rattling Skeleton, Swamp Witch, Dark Knight, Baby Dragon, Frost Knight, Frost
Shaman, Cult Priest, Mad Plague Doctor, The Goblin Foreman, Basilisk, Cursed
Dwarf, Shadow Priest, Cloud Ogre, Sky Serpent, Storm Soldier, Thunder Knight.

A block with no traits is an attack routine with ability scores attached.
Four of these are bosses.

---

## C. You cannot find anything in it

### C1. Neither index has page numbers

"Monsters by name" gives name and CR. "Monsters by challenge rating" gives
name, world and size. Neither says what page the creature is on.

To look up the Bog Hag in a 146-page book: find her in the A–Z (learn her
CR), cross-reference the CR table (learn her world), then the contents (learn
where that world starts), then leaf. Three lookups and a hunt, for the single
most common thing anyone does with a bestiary.

The two-pass build already records page positions for the contents. The data
exists and is not being used.

### C2. No index by creature type

A DM building an undead encounter, or picking something for a cleric to turn,
or checking what a ranger's favored enemy covers, wants the 26 undead listed
together. There are 14 types in the book and no way to see them grouped.

### C3. No index by terrain

The selling line is "drop any creature into whatever game you are already
running." The worlds are the game's geography, not D&D's. A DM running their
own campaign wants arctic, desert, coast, swamp, underground, forest, urban
and planar — which the ten worlds map onto almost one to one, but nobody has
written the mapping down.

### C4. No at-a-glance table

One page listing all 168 with CR, AC, HP and page number is the page that
ends up photocopied and clipped inside the DM screen. It does not exist.

---

## D. Missing DM tools

### D1. No encounter-building help

The book assigns every creature a party level and then says nothing about
spending an XP budget. There is no table of thresholds, no multiplier for
group size, no worked example. The introduction explains where the ratings
came from — which is honest and good — but never tells a DM how to use one.

### D2. No ready-made encounters

The book is already organized into forty areas, each with its own creatures
and a boss, each written for a known party level. That is a pre-built
encounter table that has not been written down. "Four Frost Knights and an
Ice Golem, 5th-level party, hard" is one line per area, forty lines total,
and it is the difference between a reference book and one a DM can run from
on a Tuesday night.

---

## What I propose to do

In this order, because each depends on the one before it:

1. **Fix A3, A4, A5, A6** — small, contained data and wording bugs.
2. **Add saving throws (A2)** by creature type and CR, SRD-style.
3. **Add legendary actions (B1)** to all forty bosses, and lair actions (B2)
   to the ten world bosses.
4. **Add spellcasting (B3)** to the nine casters, SRD spell lists only.
5. **Add traits (B4)** to the sixteen bare creatures.
6. **Re-derive the challenge ratings (A1)** last, because 2–5 change the
   numbers CR is computed from. Raise hit points and damage to the DMG bands
   rather than lowering the printed ratings — the game's own difficulty curve
   is the point of the book, so the monsters should be as hard as they claim.
7. **Add page numbers to both indexes (C1)**, plus indexes by type (C2) and
   terrain (C3), and the at-a-glance table (C4).
8. **Add encounter-building guidance (D1)** and the forty area encounters
   (D2).

Page count will grow — probably 146 to somewhere near 175. That changes the
spine width, so the KDP cover gets rebuilt too, and the interior has to be
re-uploaded.

---

## What was done

All fourteen findings, plus two more that only turned up once the first ones
were fixed.

| | Finding | Fix |
|---|---|---|
| A1 | Challenge ratings inflated | Armor class, attack bonus and damage a round now come from the DMG's table. Damage is counted as it actually arrives: a Recharge 5-6 blow lands about four rounds in seven, not every round, and a boss's legendary attack is counted. Hit points follow published creatures at the bottom and the table from challenge 13 up |
| A2 | No saving throws | Chosen by creature type and rating, SRD-style. Bosses always guard Wisdom and Constitution |
| A3 | Duplicate skills on 13 | The family merge now de-duplicates skills and senses |
| A4 | Six attacks with no dice | Life Drain, Feed and Siphon roll damage like everything else |
| A5 | Sky Serpent had no breath | Anything with a breath weapon declared now gets a heavy blow, boss or not |
| A6 | Six elementals missing darkvision | Added to the elemental family |
| B1 | No legendary actions | All forty bosses: a cheap option, an attack for two, and a board-changing option for three chosen by creature type |
| B2 | No lair actions | The ten world bosses, each tied to its own named place |
| B3 | No spellcasters | The nine named casters, SRD spells only, lists kept to what they will actually cast |
| B4 | Sixteen with no traits | One fitting SRD trait each |
| C1 | Indexes had no page numbers | Both carry them now |
| C2 | No index by kind | Added |
| C3 | No index by terrain | Added, mapping the ten worlds onto ordinary D&D terrain |
| C4 | No at-a-glance table | Added: all 168 with rating, armor class, hit points and page, on two pages |
| D1 | No encounter guidance | A chapter: XP thresholds for every party level, the crowd multiplier, and what the words mean |
| D2 | No ready-made encounters | Forty: a patrol and a boss fight for every area, costed against the party level that area was written for |

Two more, found while fixing the above:

| | Finding | Fix |
|---|---|---|
| E1 | **"The the flame fiend"** | Thirty-one creatures are named "The Something" and every piece of SRD wording supplies its own article. The name is now stripped of a leading "The" wherever it is dropped into a sentence. This was in the first build too, on all 31, and the audit missed it |
| E2 | **Every boss filed under T** | The indexes sorted "The Bog Hag" under T. They now ignore a leading article, so she is under B where someone looking for her will be |

And one latent bug in the family merge: a creature that both replaced a list
and added to it got whichever was written last in the source. The merge now
applies plain overrides first and additions second, whatever order they are
written in.

---

## Second pass: looking at the pages

The first pass checked the book by pulling its text out and measuring it.
That misses anything that is wrong only when you *look* at it, and something
was. Josh spotted it on the Troll King's page.

**F1. The rule under every section heading was struck through the heading.**
It was drawn one point *above* the baseline instead of below it, so the line
meant to underline "Actions" crossed the letters, and on "Legendary Actions"
and "Lair Actions" it cut the descenders of the g and the y. This was on all
168 stat blocks and it was in the first print too. A text dump cannot see it.

There is now a check for it — `rule through text`, in the layout checker —
along with text-on-text overlaps and margin breaches, run over every page.

Then every page was rendered and read. That turned up:

| | Found | Fix |
|---|---|---|
| F2 | The Lich and the Demon King ran off the bottom of the page. Spellcasting and lair actions made their columns taller than the page | The boss picture gives up width before the stat block does, so one boss still fits one page |
| F3 | KDP's previewer rejected page 100: text 26 pt from the trim where it wants 27 | Running head and folio moved clear |
| F4 | **"Monstrositys", "Undeads", "Feys"** in the index of kinds | Named properly instead of adding an s |
| F5 | An area's "Boss fight" line could land at the top of a page with its heading left behind on the previous one | The area's heading and both its encounters stay together |
| F6 | A world's name could sit alone at the foot of a page in the encounters list | It now needs room for its first area too |
| F7 | Section headings sat too close to the paragraph above | More air above the heading |
| F8 | The last page was blank | A closing page |

**F9, the big one: forty pages were sixty per cent white.**

Every area holds three ordinary creatures, two fill a page, so the third was
left alone on a page with nothing under it. Forty areas, forty such pages,
a median of 475 points of blank out of 792.

Three ordinary creatures will not fit on one page — measured, not assumed:
even squeezed to the tightest readable setting the median entry is 233 points
where 217 is needed, and only 42 of 128 would fit. Shrinking the boss art to
share the leftover page would have made boss pictures smaller than the mob
pictures.

So the rank and file of all four areas now run on without a break and the
world's four bosses take a page each at the end of the world. Each leftover
pairs with the first creature of the next area. Single-entry pages went from
**40 to 4**, the book from **156 pages to 138**, and no picture got smaller.
Printing drops from $7.27 a copy to $6.55, which at $29.99 is $11.45 a copy
instead of $10.72.
