# Monster Solitaire — build plan

**Read this whole page first. It is written for somebody who has not seen the
Monster Farkle work and has not read `dev/game.html` yet.**

A third game on the Axes & Aces site, at `axesandaces.com/solitaire.html`. Same
domain, same art, same videos, same music, same leaderboard, same cloud saves.

---

## What you are walking into

**Axes & Aces** is Josh's free dark-comic card RPG at axesandaces.com: you fight
monsters with poker hands. Vanilla JavaScript — no framework, no bundler, no npm
build. The whole game is one file, `dev/game.html`, which a Python script wraps
into `play.html` at the repo root.

It runs on Netlify with Neon Postgres behind four Netlify functions for the
leaderboard and cloud saves. It has about 170 monsters, each with still art plus
an idle clip and an attack clip, ten worlds of music, and 220 Facebook share
pages. There is an Android app on Google Play and an iPhone build.

Josh wants more games on the same art library, because the art and video are
already made and paid for and the audiences barely overlap. Monster Farkle was
built first — read `dev/plans/farkle.md` and the finished `dev/farkle.html`
before you start, because almost everything you need has already been solved
there once, in this exact house style.

**Josh is not a developer.** Keep anything you say to him short and plain. No
code talk, no file paths. Do everything you can yourself, and only ask him for
what genuinely needs him. Build effort costs him nothing, so never trim scope to
save work or time.

## How the code is laid out

`dev/game.html` is the single-file source: HTML, CSS and JavaScript together,
with **no `<head>`**. The doctype, head and viewport meta live in a `head`
string inside `dev/build.py`, which wraps the fragment and writes `play.html`.

Follow the same shape: source in `dev/solitaire.html`, a new target in
`dev/build.py`, output `solitaire.html` at the repo root.

**The trap that will cost you a day if you miss it.** Because the source has no
viewport meta, any test page you make by injecting into it has none either, and
a mobile-emulated Chrome then lays the page out at 980px — so every `max-width`
media query reads false. The page looks laid out while no phone CSS is live at
all. Build test pages with `python dev/gen/harness.py <source> <out>`, which
lifts the head out of `build.py` so it cannot drift. **Before you trust any
phone measurement, confirm `matchMedia('(max-width:560px)').matches` is true at
320 wide.**

`dev/gen/audit.js` finds cropped art, clipped text, overlaps and small tap
targets. `dev/gen/mobscan.cjs` drives a screen sweep with it. Use both.

Note: `harness.py` finds the head with a regex on `head = """..."""` in
`build.py`. Monster Farkle's head is a separate variable, `fhead`, and
`harness.py` picks the right one by source filename. Add `shead` the same way.

## What you may not touch

Do not edit `dev/game.html`, `dev/landing.html`, `index.html`, `play.html` or
`sw.js` beyond adding your build target to `dev/build.py`. The main game is
being changed in other sessions. Read `dev/game.html` all you like — take
whatever you want out of it — but change nothing in it.

Also leave `dev/farkle.html` alone. Copy from it freely.

## Josh's rules, all hard

- **Phone first.** Test at 390×844, 375×667, 360×740 and 320×568.
- No popup ever needs scrolling to reach its main button.
- No text on top of text. No cropped heads.
- **No emoji** anywhere a player can see. Card suits (♠ ♥ ♦ ♣) are fine — they
  are part of the cards.
- **American English only** in anything a player reads — never "colour",
  "armour", "whilst", "sorted".
- Write the address as **AxesAndAces.com**.
- No password, gate or private-preview screen on anything, ever.
- Plain words in the copy. Nothing clever, nothing jargon.
- Check every new screen and every piece of art against `BRAND.md`.
- **Do not publish to Netlify.** Josh publishes.

---

## The game: Tri-Peaks, not Klondike

**Monster Solitaire is Tri-Peaks.** Three overlapping peaks of cards sit above a
waste pile. You clear a face-up card by playing it onto the waste when it is one
rank above or below the top waste card — aces wrap both ways, so a king takes an
ace and an ace takes a two. When you are stuck, you turn a card off the stock.
Clear all three peaks and the round is yours.

Klondike was the obvious choice and it is the wrong one. A Klondike game runs
ten to twenty minutes, has long stretches where nothing happens, and about one
in five deals is unwinnable — none of which survives being a monster fight.
Tri-Peaks runs one to three minutes, and the thing that makes it good is a
**run**: each card you clear without touching the stock extends a chain, and the
chain is visibly getting bigger while you play it. That chain is the blow you
are winding up. It maps onto a monster fight exactly.

So: **Monster Farkle is push-your-luck. Monster Solitaire is the long chain.**
Two different feelings off the same art, which is the whole point of building
both.

### The narrative, and why this fight is cards laid out in peaks

The card game is poker hands at a tavern table. This is something else: a
reading. In the Gilded Ace there is a worn deck nobody deals from, and Old Bram
lays it out in three peaks when he wants to know what is coming. The cards fall,
the shape tells you the monster, and clearing the shape is how you cut your way
through to it. The longer the run you can read in one go, the harder the blow
lands when it breaks.

The worlds, areas, bosses, tavern, Anna and Old Bram are all already written in
`dev/game.html`. Build on those. Do not invent a separate world.

### Words the game uses on screen

Plain words. Nothing clever.

| On screen | What it is |
|---|---|
| **Run** | how many cards you have cleared in a row without the stock |
| **Strike!** | the blow, which lands when a run ends |
| **Peak down** | one of the three peaks fully cleared |
| **Stuck** | no legal play, so you must turn a card — and the monster hits you |
| **Clear** | all three peaks down, the round won |

### The fight loop

- The monster has health, armor and a move pattern, exactly as in
  `dev/game.html`.
- Each card you clear adds its rank value to the run, and the run length is the
  multiplier. One card is a scratch. A run of eight is a huge blow.
- A run ends when you turn a card off the stock. **That is when the blow lands**
  — the damage is the run's total times its length multiplier, cut by the
  monster's armor.
- Turning a stock card also lets the monster take its move: attack, block, heal,
  off the same pattern array the card game uses.
- **Running out of stock with peaks still standing** loses the round: the
  monster gets a free heavy hit and the layout is redealt.
- **Clearing all three peaks** is a finisher — a huge bonus blow, usually enough
  to end the fight.

So the gamble is: play the safe short run now, or hunt for the card that extends
it and risk being stuck with a worse board. Same shape of decision as the other
two games, reached a different way.

---

# The steps

Each step is finishable and checkable on its own. Commit after each one.

## 1. Read, then build the plumbing

Read `dev/plans/farkle.md`, `dev/farkle.html`, `BRAND.md` and enough of
`dev/game.html` to know where its panel system, health bars, monster intro,
level-up screen and brag pictures are.

Create `dev/solitaire.html` as a fragment with no `<head>`, the same shape as
the other two. Add a target to `dev/build.py` with its head in a **separate
variable** (`shead`) that writes `solitaire.html` at the repo root, and teach
`harness.py` to pick `shead` for that source.

**Done when:** `python dev/build.py` writes `solitaire.html` and still writes
`play.html`, `index.html` and `farkle.html` unchanged; `harness.py` builds a
test page from it; and at 320 wide on that test page,
`matchMedia('(max-width:560px)').matches` is **true**.

## 2. The deal, and prove it is always winnable enough

Three peaks of ten cards each (28 cards in the pyramid shape: 3 on top, then 6,
then 9, then a row of 10 face up), and 24 cards in the stock.

Write `dev/gen/peakdeal.cjs`: simulate a few hundred thousand deals with a
decent solver and print **what share are clearable**, the **average longest run**
and the **average number of stock cards left on a clear**. Tri-Peaks deals vary
a lot, so bias the deal — reshuffle until the deal is solvable by the solver —
so a player never gets a dead board. Monster health and monster hits in step 6
get built off these measured numbers, the way `HAND_AVG = 121` in
`dev/game.html` was measured by `dev/gen/handavg.cjs`. Do not guess them.

**Done when:** the simulator prints those three numbers, biased deals are
solvable essentially always, and both numbers are written into a comment in
`dev/solitaire.html`.

## 3. The layout, and the cards

Reuse the card look from `dev/game.html` — `art/card_face.webp`, `art/face_j`,
`face_q`, `face_k`, the suits, the rank corners. Cards must be readable at
320px wide, which for three overlapping peaks means they overlap vertically by
a lot and the rank corner is what the player actually reads. Get that right
before anything else: on a 320-wide screen every face-up card's rank and suit
must be legible without zooming.

Face-down cards get the deck back. A card that is playable right now gets a gold
ring, so the player is never hunting.

**Done when:** the three peaks, the waste and the stock all fit above the
monster-free part of the screen at all four phone sizes, with no sideways
scroll, every tap target at least 44px, and every visible rank readable.

## 4. The play loop

Tap a playable card, it flies to the waste with a snap and the run counter ticks
up. Tap the stock, a card turns and the run ends. Cards underneath flip face up
as they are uncovered, with a flip animation.

The run readout grows and gets louder as it goes — bigger numbers, a rising
tone per card, a glow that intensifies. By a run of six it should feel like
something is building.

**Done when:** a full round plays by tapping, including a long run, a stuck
board and a clear, with the run count and the legal moves correct throughout.

## 5. The monster stage

Copy it from `dev/farkle.html`, which already copied it from `dev/game.html`:
area background (`art/bg_*.webp`), monster still art (`art/<slug>.webp`),
looping idle clip (`vid/<slug>_idle.mp4`), the vertical health bar, the name,
the level badge, the threat color, the next-move chip, and the recolored-cousin
trick that turns one monster's art into several monsters. Hero strip underneath
with health, level, gold, Attack, Defense, and the portrait off
`art/hero_t0..t5.webp` by armor tier.

The hard part here is space: a solitaire layout wants height and so does the
monster. On a phone the monster sits in a short band at the top with the peaks
below it, and on a desktop the monster fills the right side with the peaks on
the left. Decide that before you build it, not after.

**Done when:** monster and peaks both fit, nothing covers the monster's head,
and the layout works at 390×844, 375×667, 360×740, 320×568 and on a desktop.

## 6. Strike: the blow lands when the run breaks

Damage = the run's total card value × the run-length multiplier × the level step
(`1.12^level`) × the Attack multiplier off the equipped weapon, then cut by the
monster's armor — the same shape as `dev/game.html`, scaled from the measured
numbers in step 2.

The sequence: the waste pile sweeps up into the blow, the axe falls, the monster
flashes white and recoils, a comic burst, the damage number counts up out of it,
the screen shakes in proportion, the health bar drains. A run of eight or more
gets the full treatment — freeze, flash, boom. A run of one stays quick.

**Done when:** a long run reads as a much bigger event than a short one, and the
health bar matches the number shown.

## 7. Stuck, and the monster hits you

Turning a stock card is a small cost: the monster takes its ordinary move. The
real punishment is running out of stock with peaks still up.

Banner, then the monster's attack clip (`vid/<slug>_attack.mp4`) with the blow
landing on the frame `HIT_AT[slug]` names, screen shake, a hurt number, health
down, cut by your Defense. Then the layout redeals.

**Done when:** the hit lands on the frame the monster swings, health drops by
what the number said, and running dry is clearly worse than turning a card.

## 8. Peak down, and the clear

Clearing one peak is a moment: that peak's cards burst, a bonus blow lands, and
the two remaining peaks slide to fill the space. Clearing all three is the
finisher — the biggest animation in the game, a huge bonus blow, and usually the
end of the fight.

**Done when:** all three happen, the layout reflows cleanly after each peak, and
the clear reads as the best thing that can happen in a round.

## 9. Fight intro and the tape

Reuse `fightIntro()` from `dev/game.html`: area art, monster in front of it, a
title tag, a line of monster talk typing in, a tape panel comparing you and it,
one big **Fight!** button. Keep the four kinds of meeting — ambush, you spot it
first, blocked path, boss.

Boss fights get a **layout rule**, the way card bosses get a dead suit and
Farkle bosses get a dice rule:

- Four peaks instead of three
- Aces do not wrap, so the chain can break dead
- Only 18 stock cards instead of 24
- One peak starts fully face down
- A run resets at five, however good the board looks

**Done when:** all four intros fit a 320×568 screen with Fight! reachable
without scrolling, and a boss rule visibly changes the round.

## 10. Victory, gold and experience

Reuse `victoryPanel()`: the defeated monster's `art/dead_<slug>.webp`, the gold
purse counting up, the experience bar filling, the drop, the health bar, and a
brag button on a boss. Keep **Flawless** (took no damage, double gold) and
**Clutch** (won on your last sliver). Solitaire gets its own: **Clean Read**,
for clearing all three peaks without running the stock dry.

**Done when:** a win plays through with the numbers counting up, fitting on a
320-wide screen.

## 11. Level up

Reuse `levelPanel()` and the ladder — `1.12` per level, the experience needs,
the medal, the stat rows counting up, a choice of perk. The perks become
solitaire perks:

- **Long Memory** — runs of five or more count double
- **Second Sight** — see the next stock card before you turn it
- **Deep Deck** — +3 stock cards
- **Wild Ace** — once a round, play any card onto an ace
- **Tough as Nails** — +10 max health
- **Training** — more experience from every fight

**Done when:** a level-up fits a 320-wide screen with no clipped numbers, and
each perk measurably changes the next round.

## 12. Gear, from the smith

Reuse `EQUIP` and its icon art exactly: sword, battle axe, dagger, shield,
helmet, armor, five material tiers each, icons at `art/i_eq_*.webp`. Attack
multiplies the blow. Defense cuts what being stuck costs you. Armor tier drives
the hero portrait.

**Done when:** a better axe visibly raises the strike number, armor visibly
lowers the damage taken, and the portrait changes with the tier.

## 13. Charms and potions

Potions come straight across — healing, iron skin, rage. The charms are
solitaire's own:

- **Marked Deck** — one peak starts one card shallower
- **Jester's Coin** — once a round, send the waste card back and keep the run
- **Reader's Glass** — see one face-down card at the start
- **Gambler's Ring** — +25% damage on a run of six or more
- **Iron Cup** — start every round with block

**Done when:** each charm works, each says plainly what it does, and the pouch
row fits a 320-wide screen.

## 14. The merchant

Reuse `shopPanel()` and its tabs — smith, charms, potions. Same gold, same price
shape, same cannot-afford look, same coins-leaving-the-purse animation.

**Done when:** you can buy in all three tabs, gold goes down correctly, and the
panel never needs scrolling to reach its main button.

## 15. Worlds, areas and the path

Copy the `WORLDS` data out of `dev/game.html` — ten worlds, four areas each,
with pools, bosses, place names, story and area icons — and the world-loading
code. Keep the Rescue of Anna as world one and the Endless depths past ten.
Reuse `pathPanel()` so you choose where to go next.

**Done when:** you can clear an area, pick a path, cross into the next area with
its own background and music, and finish a world into the next one.

## 16. The deck back, one per world

The flavor the cards are allowed to have, as CSS only: a deck back per world —
bone, frost, desert, sunken, iron, ember, bog, grave, storm, gold. The faces
never change. The faces are what the player reads, and a face that is harder to
read at 320px is wrong whatever it looks like.

**Done when:** all ten backs read clearly at 320px and no face has been touched.

## 17. The story panels

Reuse `storyPanel()`, `runCine()` and the scene art (`art/sc_*.webp`) with the
typing caption. Rewrite the three or four beats per world so they are about the
reading rather than the card table or the dice table, keeping the same
characters and places.

**Done when:** every story panel fits a 320×568 screen with its Next button
reachable, and no text sits on other text.

## 18. Music

Reuse `music/w1..w10.mp3`, `boss.mp3`, `fight1.mp3`, `fight2.mp3`, the crossfade
code and the sound menu. Add the card sounds: the slap of a card onto the waste,
the flip of one turning face up, a rising tone per card in a run, a burst on a
peak down, a dead thud on running dry.

**Done when:** music follows the world and the boss, the toggles stick between
visits, and nothing clips or overlaps.

## 19. Saves, slots, cloud and the leaderboard

Three save slots under their own keys (`sl_*`, so Solitaire can never overwrite
an Axes & Aces or a Monster Farkle hero). Reuse the cloud-save code and the same
private code format against `netlify/functions/save-game.mjs` and
`load-game.mjs` — they store whatever JSON they are handed, so no change is
needed there.

The leaderboard needs one additive change: `add-score.mjs` and `get-scores.mjs`
accept a fixed list of `board` values. Monster Farkle added `farkle` and
`farkle_daily`; add `solitaire` and `solitaire_daily` the same way. The `scores`
table already has the columns, so there is no migration.

**Done when:** a hero survives a reload, a cloud code restores it on a fresh
browser, and a score posts to the Solitaire board and comes back in the list.

## 20. Brag cards

Reuse `bragCard()` — the 1200×630 comic card, scene behind, figure on the right,
gold headline, and **PLAY FREE ▸ AxesAndAces.com** spelled exactly that way.
Solitaire's own moments: longest run, a boss down, a level reached, how far you
got before you fell.

Add the brag pages under `b/` the way `dev/gen/bragpages.py` makes them, with
`sol_` keys so they never collide, each pointing at
`axesandaces.com/solitaire.html`.

**Done when:** a card renders with no clipped text, the address reads
AxesAndAces.com, and the share page redirects to the Solitaire page.

## 21. Guide and help

A short how-to-play: one above or below, aces wrap, clear the peaks, long runs
hit harder. Reuse `guidePanel()` and `helpPanel()`.

**Done when:** it is readable on a 320-wide screen without sideways scrolling,
and the first-time coaching marks explain play, stock, run and clear in that
order.

## 22. The daily challenge

Same seeded deal for everybody: five fights, the same monsters and the same
deals for every player that day, posting to the Solitaire daily board. Reuse
the seeded random and the daily code from `dev/game.html`.

**Done when:** two fresh browsers on the same day get identical deals, and a
score posts and comes back.

## 23. The phone sweep

Write `dev/gen/slscan.cjs` the way `dev/gen/mobscan.cjs` works: build the test
page with `harness.py`, drive every screen through `window.__A.ev`, run
`dev/gen/audit.js` on each, and save a screenshot per screen per size.

Screens: hero select, story, all four fight intros, mid-round, a long run, a
peak down, a clear, stuck, strike, victory, level up, all three shop tabs, path,
fallen, guide, help, menu, leaderboard, cloud save, brag.

Sizes: 390×844, 375×667, 360×740, 320×568.

Fix every finding: cropped art, clipped text, text on text, anything off the
edge, any tap target under 44px, any panel that needs scrolling to reach its
main button.

**Done when:** the sweep is clean at all four sizes with no console errors, and
the screenshots have been looked at one by one, not just the report.

## 24. Final pass against the house rules

Go back through "Josh's rules, all hard" at the top of this page, line by line,
and check each one. Then check every new screen against `BRAND.md`: 3px black
borders, hard offset shadows, Germania One for titles, Oswald for numbers,
Alegreya Sans or Vollkorn for story text, gold `#f2b632`, crimson `#c8241f`,
green `#3fae4a`.

**Done when:** Monster Solitaire plays start to finish on a phone and on a
desktop from `solitaire.html`, committed, with the sweep clean.

---

## Left for Josh

- **Publishing.** Do not publish to Netlify. Josh publishes, and he has a
  one-publish-a-day limit.
- **A link from the front page.** `dev/landing.html` and `index.html` are out of
  bounds, so Monster Solitaire will have no link from the front page. Josh or a
  later session adds it, along with the Monster Farkle link.
- **`sw.js`** does not cache `solitaire.html`, for the same reason.

## If you need new art

Everything you need is already in the repo: `art/` has 580 pictures,
`vid/` has 413 clips, `music/` has 13 songs. All paid for.

If you genuinely need something new, Kie AI (the `kie` MCP server, prepaid) is
the right tool because it can match the existing painted comic style. Pexels is
available and free but photographs fight `BRAND.md`'s inked comic look, so it is
almost certainly wrong here. Figma is paid for and available if a screen needs
designing before it is built. Tell Josh the cost before spending anything on
generation.
