# Monster Farkle — build plan

A second game on the Axes & Aces site, at `axesandaces.com/farkle.html`. Same
domain, same art, same videos, same music, same leaderboard, same cloud saves.

Farkle is public domain — no owner, no trademark — so it keeps its real name.

## The idea in one line

Six dice. The turn's total is the blow you are winding up. Strike and the
monster takes it. Farkle and the monster hits you instead.

## The narrative, and why this fight is dice

Old Bram keeps a soldier's set of bone dice behind the bar at the Gilded Ace —
six knuckles off something that used to be a dragon. A knight's dice, not a
gambler's. You do not play cards at this table. You wind up a swing: every die
you keep adds force to the blow, and the longer you push the harder it lands.
Push too far and your guard drops, and whatever you are fighting gets its hit
in first.

That is the same gamble the card game already runs on — risk the turn to hit
harder — and it suits dice better than it suits cards, because in Farkle the
risk is on every single roll instead of once a hand.

The worlds, areas, bosses, tavern, Anna and Old Bram are already written in
`dev/game.html`. Build on those. Monster Farkle is the dice table in the back
of the Gilded Ace, not a separate world.

## Words the game uses on screen

Plain words, Josh's rule. Nothing clever.

| On screen | What it is |
|---|---|
| **Wind-up** | the turn's running total, not yet banked |
| **Roll** | roll the dice that are not set aside |
| **Strike!** | bank the wind-up and hit the monster for it |
| **FARKLE!** | a roll that scores nothing. Wind-up lost, monster hits you |
| **Hot dice** | all six dice scored, so you get all six back and keep rolling |
| **Set aside** | the scoring dice you keep |

## The scoring, which is the real Farkle scoring

| Combination | Scores |
|---|---|
| Each 1 | 100 |
| Each 5 | 50 |
| Three 1s | 1000 |
| Three 2s / 3s / 4s / 5s / 6s | face × 100 |
| Four of a kind | 1000 |
| Five of a kind | 2000 |
| Six of a kind | 3000 |
| Straight, 1 through 6 | 1500 |
| Three pairs | 1500 |
| Two triplets | 2500 |
| Four of a kind plus a pair | 1500 |

Only 1s and 5s score on their own. Everything else has to be part of a set.

**The dice keep ordinary readable pips.** No monster faces on dice faces — that
is the one change that would sink the whole game, because the player has to read
six dice at a glance. The flavor goes in the material of the dice, the names of
the combinations, and what happens around the roll.

---

# The steps

Each step is finishable and checkable on its own. Commit after each one.

## 1. Build plumbing, and prove the phone CSS is live

Create `dev/farkle.html` as a **fragment with no `<head>`**, the same shape as
`dev/game.html`: `<title>`, font links, `<style>`, the body markup, then one
`<script>` holding an IIFE.

Add a target to `dev/build.py` that wraps it and writes `farkle.html` at the
repo root. Its head string must be a **separate variable** (`fhead`), not a
second `head =`, because `dev/gen/harness.py` pulls the game's head out of
`build.py` with a regex on `head = """..."""` and two of them would break it.
Teach `harness.py` to use `fhead` when the source is `dev/farkle.html`, so the
test page's head can never drift from the real one.

Do not touch `dev/game.html`, `dev/landing.html`, `index.html`, `play.html` or
`sw.js` beyond adding this target.

**Done when:** `python dev/build.py` writes `farkle.html` and still writes
`play.html` and `index.html` unchanged; `python dev/gen/harness.py
dev/farkle.html farkletest.html` works; and in a 320-wide mobile-emulated Chrome
on `farkletest.html`, `matchMedia('(max-width:560px)').matches` is **true**.
Check that before trusting any phone measurement — without a viewport meta the
page lays out at 980px and every `max-width` query silently reads false.

## 2. The scoring engine, and measure what a turn is worth

Pure functions, no DOM:

- `scoreRoll(faces)` → every combination present, the best-scoring split, the
  dice each combination uses, and the leftover dice.
- `bestSplit(faces)` → the highest total you can take from this roll.
- `isFarkle(faces)` → true when nothing scores.
- `scoreOf(kept)` → what a chosen set of dice is worth, and whether the choice
  is legal (every kept die must belong to a scoring combination).

Then write `dev/gen/dieavg.cjs`: simulate a few hundred thousand turns with a
sensible player (keep the best split, roll again while the wind-up is under a
threshold, bank above it) and print the **average banked wind-up** and the
**farkle rate**. Monster health and monster hits in step 6 get built off that
measured number, the way `HAND_AVG = 121` in `dev/game.html` was measured by
`dev/gen/handavg.cjs`. Do not guess it.

**Done when:** a node check prints the right score for every known case (six 1s
= 3000, 1-2-3-4-5-6 = 1500, 2-2-3-3-4-4 = 1500, 1-1-1-5-5-5 = 2500, 4-4-4-4-2-2
= 1500, 2-3-4-6 = farkle), and `dieavg.cjs` prints an average wind-up and a
farkle rate. Write both numbers into a comment in `dev/farkle.html`.

## 3. The dice tray, and the tumble

Six dice in the tray. A die is a rounded square with pips in a 3×3 grid — big,
high contrast, readable at 320px wide. Not an image, not a font, not an emoji.

The roll:
- each die gets a tumble that spins and bounces, with the pip face swapping a
  few times mid-tumble so it reads as a real roll;
- dice are staggered about 60ms apart so they land one after another;
- each landing overshoots slightly, then settles, with a dice-on-wood knock;
- dice that can score land with a gold ring; dice that cannot stay plain.

Tapping a scoring die sets it aside: it slides to the set-aside row with a snap
and the wind-up readout counts up. Tapping it again takes it back. Respect
`prefers-reduced-motion` — no tumble, just the result.

**Done when:** the tray reads clean and the pips are unmistakable at 390×844,
375×667, 360×740 and 320×568, with no horizontal scroll and every die at least
44px tall.

## 4. The turn loop

Roll → set aside → roll again → Strike, over and over.

- **Roll** rolls only the dice not set aside.
- You may only roll again if you set at least one scoring die aside this roll.
- **Hot dice:** when all six dice end up set aside, all six come back and you
  keep rolling with the wind-up intact. Shout "Hot dice!" and flash all six gold.
- **Farkle:** a roll where nothing scores. Wind-up lost, turn over.
- **Strike** banks the wind-up.

The buttons are **Roll** and **Strike!**, side by side, thumb-sized, and Strike
shows what it will hit for. Roll shows the risk: how many dice are coming back.

**Done when:** a full turn plays by tapping — including a hot-dice chain and a
farkle — with the wind-up correct at every point, and the illegal moves are
impossible rather than merely discouraged.

## 5. The monster stage

Reuse it from `dev/game.html`: the area background (`art/bg_*.webp`), the
monster's still art (`art/<slug>.webp`), the looping idle clip
(`vid/<slug>_idle.mp4`), the vertical health bar, the name, the level badge, the
threat color, and the next-move chip. Copy `VIDS`, `HIT_AT`, `ART`, `TINT` and
the recolored-cousin trick straight across — the cousins are free monsters.

Hero strip underneath: health bar, level, gold, Attack and Defense, the soldier
portrait off `art/hero_t0..t5.webp` by armor tier.

**Done when:** a monster stands there breathing, with its idle clip playing and
nothing covering its head, at all four phone sizes and on a desktop.

## 6. Strike: the axe lands

Banking the wind-up is the payoff, so spend the animation budget here.

Damage = wind-up × the level step (`1.12^level`) × the Attack multiplier off the
equipped weapon, then cut by the monster's armor — the same shape as
`dev/game.html`, but scaled from Farkle's own measured average wind-up from
step 2, not from `HAND_AVG`.

The sequence: the dice sweep off the tray, the axe falls, the monster flashes
white and recoils, a comic burst, the damage number counts up out of it, the
screen shakes in proportion to the size of the hit, and the monster's health bar
drains. Big hits get a bigger shake, a freeze and a boom; ordinary hits stay
quick.

**Done when:** a strike reads as a blow landing, three sizes of hit feel
different, and the monster's health bar matches the number shown.

## 7. Farkle: the monster hits you

A farkle has to hurt, or there is no gamble.

Banner "FARKLE!" with "Your guard drops" under it. The dice all go gray and
rattle. The monster's attack clip plays (`vid/<slug>_attack.mp4`), the hit lands
on the frame `HIT_AT[slug]` says it lands on, and at that exact moment: screen
shake, a hurt number, and your health bar drops. Damage taken is cut by your
Defense, the same formula the card game uses.

**Done when:** the hit lands on the frame the monster actually swings, your
health drops by what the number said, and a farkle at full health is survivable
while a farkle at low health kills you.

## 8. The monster's move

After a strike, the monster takes its turn from its pattern: attack, raise a
block, or heal, read off the same `moves` array shape as `dev/game.html`. The
next-move chip says which is coming, so pushing your luck is an informed choice.
A block soaks your next strike. A heal gives health back.

**Done when:** a fight goes several rounds, the chip always tells the truth, and
blocks and heals both visibly do something.

## 9. Fight intro and the tape

Reuse the shape of `fightIntro()`: the area art, the monster in front of it, a
title tag, one line of monster talk typing in, the tape panel comparing you and
it, and one big **Fight!** button. Keep the four kinds of meeting — ambush, you
spot it first, blocked path, boss.

Boss fights get a **dice rule**, the way card bosses get a dead suit:

- 1s score 50, not 100
- No hot dice — six scoring dice end your turn
- A farkle costs you double
- Three of a kind scores half
- You must roll at least three times before you can strike

Four of those per world, across the ten worlds.

**Done when:** all four intros fit on a 320×568 screen with Fight! reachable
without scrolling, and a boss rule visibly changes the scoring during the fight.

## 10. Victory, gold and experience

Reuse `victoryPanel()`: the defeated monster's `art/dead_<slug>.webp`, the gold
purse counting up, the experience bar filling, the drop, the health bar, and a
brag button on a boss. Keep **Flawless** (took no damage — double gold) and
**Clutch** (won on your last sliver of health). Farkle gets one of its own:
**Hot Streak**, for banking three strikes in a row without a farkle.

**Done when:** a win plays through with the numbers counting up and the panel
fitting on a 320-wide screen.

## 11. Level up

Reuse `levelPanel()` and the ladder: `1.12` per level, experience needs, the
medal, the stat rows counting up, and a choice of perk. The perks become dice
perks:

- **Steady Hand** — +50 to every wind-up you bank
- **Lucky Bones** — your first farkle each fight costs nothing
- **Seventh Knuckle** — +1 die, so you roll seven
- **Tough as Nails** — +10 max health
- **Strong Arm** — strikes hit harder
- **Training** — more experience from every fight

**Done when:** a level-up fits on a 320-wide screen with no clipped numbers, and
each perk measurably changes the next fight.

## 12. Gear, from the smith

Reuse `EQUIP` and its icon art exactly: sword, battle axe, dagger, shield,
helmet, armor, five material tiers each, with `art/i_eq_*.webp` for the icons.
Attack multiplies the wind-up when you strike. Defense cuts what a farkle costs
you. Armor tier drives the hero portrait, same as the card game.

**Done when:** buying a better axe visibly raises the strike number, buying
armor visibly lowers the farkle damage, and the portrait changes with the tier.

## 13. Dice charms and potions

Potions come straight across — healing, iron skin, rage. The charms are Farkle's
own, and they are where the dice flavor lives:

- **Loaded Die** — once a fight, turn one die to any face
- **Bone Charm** — your first farkle each fight does no damage
- **Second Wind** — once a fight, re-roll a farkle
- **Weighted Set** — each 1 scores 150 instead of 100
- **Gambler's Ring** — +25% damage on a wind-up over 1000
- **Iron Cup** — start every turn with block

**Done when:** each charm works, each says plainly what it does, and the
pouch row fits on a 320-wide screen.

## 14. The merchant

Reuse `shopPanel()` and its tabs: the smith for gear, the charm seller, the
potion seller. Same gold, same prices shape, same "you cannot afford this" look,
same coins-leaving-the-purse animation.

**Done when:** you can buy in all three tabs, gold goes down by the right
amount, and the panel never needs scrolling to reach its main button.

## 15. Worlds, areas and the path

Copy the `WORLDS` data out of `dev/game.html` (ten worlds, four areas each, with
pools, bosses, place names, story and area icons) and the world-loading code.
Keep the Rescue of Anna as world one and the Endless depths past ten. Reuse
`pathPanel()` so you choose where to go next.

**Done when:** you can clear an area, pick a path, cross into the next area with
its own background and music, and finish a world into the next one.

## 16. The dice material, one per world

The flavor the dice are allowed to have. A set per world, as CSS only — face
color, pip color, edge, sheen:

bone, frost-cut crystal, desert stone, sunken coral, blackened iron, ember
glass, bog amber, grave marble, storm quartz, and gold for the last world.

Pips stay maximum contrast in every single one. If a set makes the pips harder
to read at 320px, the set is wrong, not the rule.

**Done when:** all ten read clearly at 320px wide, checked one by one.

## 17. The story panels

Reuse `storyPanel()`, `runCine()` and the scene art (`art/sc_*.webp`) with the
typing caption. Rewrite the three or four beats per world so they are about the
dice table rather than the card table, keeping the same characters and the same
places.

**Done when:** every story panel fits a 320×568 screen with its Next button
reachable, and no text sits on other text.

## 18. Music

Reuse `music/w1..w10.mp3`, `boss.mp3`, `fight1.mp3` and `fight2.mp3` with the
same crossfade code and the same sound menu (music, sound effects, narrator).
Add the dice sounds: the knock of dice landing, the snap of a die set aside, the
rising rattle of a hot-dice chain, and a dead thud on a farkle.

**Done when:** music follows the world and the boss, the toggles stick between
visits, and nothing clips or overlaps.

## 19. Saves, slots, cloud and the leaderboard

Three save slots under their own keys (`fk_*`, so Farkle can never overwrite an
Axes & Aces hero). Reuse the cloud-save code and the same private code format
against `netlify/functions/save-game.mjs` and `load-game.mjs` — they store
whatever JSON they are given, so no change is needed there.

The leaderboard needs one additive change: `add-score.mjs` and `get-scores.mjs`
only accept `board` of `daily` or `level`. Add `farkle` (highest level) and
`farkle_daily`. The `scores` table already has the columns, so there is no
migration — just widen the allowed values at both ends.

**Done when:** a hero survives a reload, a cloud code restores it on a fresh
browser, and a score posts to the Farkle board and comes back in the list.

## 20. Brag cards

Reuse `bragCard()` — the 1200×630 comic card, scene behind, figure on the right,
gold headline, and **PLAY FREE ▸ AxesAndAces.com** spelled exactly that way.
Farkle's own moments: biggest single strike, a boss down, a level reached, how
far you got before you fell.

Add the brag pages under `b/` the way `dev/gen/bragpages.py` makes them, with
`farkle_` keys so they never collide, each pointing at `axesandaces.com/farkle.html`.

**Done when:** a card renders with no clipped text, the address reads
AxesAndAces.com, and the share page redirects to the Farkle page.

## 21. Guide and help

A scoring table with real little dice pictures for every combination, and a
short how-to-play. Reuse `guidePanel()` and `helpPanel()`.

**Done when:** the whole scoring table is readable on a 320-wide screen without
sideways scrolling, and the first-time coaching marks explain roll, set aside,
strike and farkle in that order.

## 22. The daily challenge

Same seeded run for everybody: five fights, the same monsters and the same dice
rolls for every player that day, posting to the Farkle daily board. Reuse the
seeded random and the daily code from `dev/game.html`.

**Done when:** two fresh browsers on the same day get identical dice, and a
score posts and comes back.

## 23. The phone sweep

Write `dev/gen/fkscan.cjs` the way `dev/gen/mobscan.cjs` works: build the test
page with `harness.py`, drive every screen through `window.__A.ev`, run
`dev/gen/audit.js` on each, and save a screenshot per screen per size.

Screens to sweep: hero select, story, all four fight intros, mid-turn with dice
set aside, hot dice, farkle, strike, victory, level up, all three shop tabs,
path, fallen, guide, help, menu, leaderboard, cloud save, brag.

Sizes: 390×844, 375×667, 360×740, 320×568.

Fix every finding: cropped art, clipped text, text on text, anything off the
edge, any tap target under 44px, and any panel that needs scrolling to reach its
main button.

**Done when:** the sweep is clean at all four sizes with no console errors, and
the screenshots have been looked at one by one, not just the report.

## 24. Final pass against the house rules

- Phone first, checked at all four sizes.
- No popup needs scrolling to reach its main button.
- No text on text. No cropped heads.
- No emoji anywhere a player can see.
- American English only — never "colour", "armour", "whilst", "sorted".
- The address is written **AxesAndAces.com**.
- No password, gate or private-preview screen on anything.
- Plain words. Nothing clever, nothing jargon.
- Every new screen checked against `BRAND.md`: 3px black borders, hard offset
  shadows, Germania One for titles, Oswald for numbers, Alegreya Sans or
  Vollkorn for story text, gold `#f2b632`, crimson `#c8241f`, green `#3fae4a`.

**Done when:** Monster Farkle plays start to finish on a phone and on a desktop
from `farkle.html`, committed, with the sweep clean.

---

---

# What changed while building it

The plan above is what was intended. These are the places the build went a
different way, and why. Everything else was built as written.

- **Four of a kind does not score a flat 1000.** Each die past the third
  doubles the three of a kind instead, so four 1s are 2000 and six 1s are 8000.
  A flat 1000 would have made four 1s worth exactly what three 1s are worth, so
  the fourth die earned nothing.
- **Guards and heals are priced off what a turn delivers**, not off the
  monster's own health. At the card game's 15% of health a monster healed more
  than a strike did and could not be killed.
- **Armor is divided back out of monster health**, so it does not lengthen a
  fight twice over. Without that a heavy monster took fifteen strikes.
- **Monster hits are a tenth of what a hero can take**, measured, not picked.
  A ninth killed a bare hero every time; a thirteenth left a careful player
  unable to lose.
- **A boss is 1.45x health, not 1.9x.** At 1.9 it ran ten strikes against a
  normal fight's six, and the player meets it already hurt.
- **No "Seventh Knuckle" perk.** Seven dice across a 320px screen come out at
  38px, under the 44px tap floor. A seventh die is not worth breaking the one
  thing the whole game rests on.
- **The merchant offers three charms a visit, not all six.** Six rows spill a
  320x568 screen, and three is a choice while six is a catalog.
- **Sound lives in the menu, not the top bar.** Four buttons and the title
  wrapped to a second row at 320, costing 38px the monster needed.
- **Losing keeps your level, gear and charms** and sends you back to the start
  of the quest. A full wipe is a reason to close the tab.
- **The daily challenge gives the player level 3 and a full set of tier-2
  gear**, so the run is about the dice and nothing else.

## How it is checked

Five tools, all in `dev/gen/`, all run against the real page rather than a copy:

- `dieavg.cjs` lifts the scoring block out of `dev/farkle.html`, checks it
  against 24 cases, and plays 300,000 turns at each of twelve thresholds.
- `fkbalance.cjs` lifts the scoring **and** the fight maths and plays whole
  fights, by level, by gear tier and against bosses.
- `fkplay.cjs` plays the real page by tapping, and catches stalls, buttons left
  disabled and health going the wrong way.
- `fkdaily.cjs` opens two clean browsers and proves they get the same day.
- `fkscan.cjs` sweeps 25 screens at four phone sizes with `audit.js`, and also
  checks that no popup needs scrolling to reach its main button.

## Left for Josh

- **Publishing.** Do not publish to Netlify. Josh publishes.
- **A link from the front page.** `dev/landing.html` and `index.html` are out of
  bounds while the main game is being changed in another session, so Monster
  Farkle will have no link from the front page. Josh or a later session adds it.
- **`sw.js`** does not cache `farkle.html`, for the same reason.
