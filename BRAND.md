# Axes & Aces: Brand Brief

Design every screen, button, picture, post and video against this page. If something doesn't fit, change it to fit.

## The idea in one line
A dark comic-book card adventure: you fight monsters with poker hands.

## Personality
- **Bold and punchy:** like a comic book cover. Big shapes, thick ink, confident moves.
- **Dark but fun:** taverns, crypts and dragons, never gory. Monsters get knocked out, not killed.
- **Warm:** the tavern, Anna and Old Bram make it feel like home.
- **Rewarding:** big hands feel huge. Small moments stay quick.

## Look

### Illustration
- Dark comic book style: thick black ink outlines, hard cel shading, halftone dots.
- Rich, saturated colors with deep crimson, gold and teal accents.
- Characters and items are cut out and sit inside real scenes, never on a blank background.
- One creature per picture, with correct anatomy (one head!).
- No text, signs or logos inside the art.

### Colors
| Use | Color |
|---|---|
| Background, panels | Soot black `#14100d`, dark leather `#1b1410` |
| Ink (outlines, shadows) | Pure black `#000` |
| Headlines, money, rewards | Gold `#f2b632` / bright gold `#ffd35c` |
| Paper (story text, tips, cards) | Parchment `#f3e6c8` with dark ink `#16100d` |
| Monster health, danger | Crimson `#c8241f` |
| Your health, healing, success | Green `#3fae4a` / `#7be38a` |
| Magic, experience | Teal `#7fe3d8` |
| Boss | Purple `#a63de0` |
| Sharing (Facebook) | Facebook blue `#1877f2`, only on share buttons |

### Type
- **Germania One:** titles, names, big moments ("Victory!", "FLAWLESS"). Never for long text.
- **Oswald (bold, uppercase, letter-spaced):** numbers, labels, buttons, stats.
- **Alegreya Sans:** story text, tips, descriptions.

### Shapes
- **Comic panels:** 3px black border, slightly rounded corners (8–12px), hard offset shadow (4px 4px 0 black). No soft blurry shadows.
- **Title tags:** gold label, black border, tilted a few degrees, top-left of a scene.
- **Speech:** parchment bubbles with a black border and a tail, placed so they never cover titles or other text.
- **Badges:** round comic medallions (level, coins), never flat squares.
- **Big numbers:** burst out of comic "POW" stars.

### Icons
- Use the game's own painted icons (coin, heart, shield, sword, potion, skull, map…).
- **No emoji anywhere** in the game, posts or videos. Card suits (♠ ♥ ♦ ♣) are allowed because they're part of the cards.

## The logo

Three separate pieces. They are not interchangeable, and everything built in
this world uses them.

| Piece | File | What it is |
|---|---|---|
| **The word logo** | `img/logo-wide.webp` (1440x638, transparent) | The full lockup: a painted double-headed battle axe on the left, **AXES & ACES** in gold slab-serif capitals in the middle, and an Ace of Hearts on the right, all on a dark rounded plaque. Also `dev/gen/out/logo/logo-wide.png` and `banner.png` (1200x630) for sharing. |
| **The icon** | `icons/icon-512.png`, `icon-192.png`, `icon-180.png`, `maskable-512.png` | Square. An Ace of Hearts behind a bold crossed double axe in crimson, teal and gold on soot black. Flatter and more graphic than the word logo's painted axe. This is the app icon and the favicon. |
| **The emblem** | `img/emblem-64.webp` (88x88) | The icon cropped in tight, for sitting inline next to a line of text. |

Rules:

- **The word logo is the title.** It goes at the top of a page, on a cover, on
  a title screen. Never retype "Axes & Aces" in some other typeface when the
  word logo would do.
- **The icon is the mark.** App icon, favicon, store tile, the corner of a
  share picture, anywhere square and small. Never squash the word logo into a
  square to make an icon.
- **Never stretch either one.** Scale both sides together or leave it alone.
- **Give it room.** Clear space all round of at least the height of the "A".
- **It sits on dark.** Soot black `#14100d` or dark leather `#1b1410`. On
  anything pale, use the plaque behind it rather than the bare lettering.
- **Don't recolor, outline, add a glow, or set it at an angle.**

### Other games and products in this world

Axes & Aces is the first thing with this name, not the only one. A sister game
or a book is **family, not a copy**:

- Keep the gold slab-serif capitals, the soot-black ground, the gold and
  parchment colors, and the painted-prop-on-dark feel.
- Build its own mark out of **its own object** - dice for a dice game, a card
  fan for a card game - sitting with the Ace the way the axe does.
- Do not put the Axes & Aces word logo on a product that is not Axes & Aces.
  Put its own name in the same family of lettering, and use the icon or emblem
  as the small "same people made this" mark.

#### Monster Farkle

The first sister game, at `farkle.html`. Its object is dice.

| Piece | File | What it is |
|---|---|---|
| **The mark** | built in the page, from `img/farkle-dice.webp` | The painted dice on the left, **MONSTER FARKLE** in gold slab capitals in the middle, an Ace of Hearts on the right, on the same dark plaque. The lettering is SVG, not a picture of lettering, so it stays sharp at any size and can never come out misspelled. |
| **The icon** | `icons/farkle-512.png`, `farkle-192.png`, `farkle-180.png`, `farkle-maskable-512.png` | Square. An Ace of Hearts behind three dice in crimson, teal and gold on soot black — the axe's place taken by dice. Its favicon and app tile. |
| **The emblem** | `img/farkle-emblem.webp` (88x88) | The icon cropped in tight, for the top bar. |
| **The banner** | `b/farkle.jpg` (1200x630) | What Facebook fetches for a Monster Farkle link. Rendered from the game's own mark by `dev/gen/fkbanner.cjs`, so it cannot drift from the start screen. |

The slab face is **Alfa Slab One**, used for the mark and nowhere else — the
rest of the game is Germania One, Oswald and Alegreya Sans as usual.

The Axes & Aces emblem appears on the start screen, in the share banner and on
every brag picture, small, as "An Axes & Aces game". It is never Monster
Farkle's own identity.

`dev/gen/fkbrand.py` rebuilds every one of these from the two source pictures
in `dev/gen/out/brand/`.

## Motion and sound
- Things slam in with a small overshoot, then settle.
- The bigger the moment, the bigger the effect: shake, flash, freeze, boom. Normal hits stay quick.
- Respect "reduce motion".
- Music: recorded orchestral and folk songs, one per world plus a boss song. Never cheesy chiptune.

## Voice
- Short, plain sentences. Talk like a friendly tavern keeper, not a manual.
- Name things the way players see them: "Attack", "Discard", "Rest", "the merchant".
- Celebrate the player ("Brutal!", "Flawless!") but never mock them when they lose.
- Old Bram teaches. Anna cheers. Monsters taunt briefly.

## Layout rules
- **Phone:** everything stacked, one hand of cards, big tap targets.
- **Desktop:** the monster fills the screen. Your health, gear and buttons sit around the edges, and nothing covers the monster's face.
- Text never sits on top of other text, and no screen needs scrolling to reach its main button.
- Every picture shows its subject's whole head and body. Never crop off heads.

## Sharing
- Brag pictures are 1200×630 comic cards: scene behind, hero or monster on the right, big gold headline, and "PLAY FREE ▸ AxesAndAces.com".
- Always write the address as **AxesAndAces.com**.
- Videos are vertical (1080×1920), 10 seconds, with a hook line at the top, the monster in the middle and "Play free at AxesAndAces.com" at the bottom. No colored boxes behind text, just outlined lettering.
