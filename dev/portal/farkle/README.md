# Monster Farkle, packaged for the games portals

Builds a self-contained package of Monster Farkle for CrazyGames and for
Poki. It reads `dev/farkle.html` and writes `dist/farkle-<portal>/`. It does
not touch `dev/build.py`, the live site, or anything the site build produces.

Everything the portal build changes is an exact-match patch applied at build
time. If `dev/farkle.html` moves under it the build **stops and says which
patch missed** rather than quietly shipping a half-converted game.

## The files

| File | What it does |
|---|---|
| `build.py` | The build. One portal per run. |
| `shim.js` | The one layer between the game and whichever portal is hosting it. |
| `fonts.py` | Pulls the game's four Google fonts into `fonts/` and writes `faces.css`. Already run; re-run only if the game changes typeface. |
| `encvid.py` | Re-encodes `vid/` small enough for CrazyGames. Needs ffmpeg. |
| `check.cjs` | Drives the built package in a browser and proves it works. |
| `covers.cjs` | Renders the store covers from the game's own mark. |
| `shots.cjs` | Screenshots of the real package, checked before they are kept. |
| `trailer.cjs` | Records the two preview videos while a bot plays. |

## Building both

```
python dev/portal/farkle/encvid.py --out .vid-small          # once, ~20 min
python dev/portal/farkle/build.py crazygames --vid .vid-small --zip
python dev/portal/farkle/build.py poki --zip
node dev/portal/farkle/check.cjs crazygames
node dev/portal/farkle/check.cjs poki
```

`dist/` and `.vid-small/` are gitignored: 200MB and 147MB of build output.

## What is different in a package, and why

- **The fonts travel with it.** Neither portal allows a font CDN at run time,
  and Poki name Google Fonts specifically.
- **Nothing links off the page.** The mark in the bar and the menu row both
  went back to the card game's site. In a package there is no site to go to,
  so the mark stays and stops being a link, and the row is gone.
- **The poster, not the share.** Sharing carries a link, so the panel just
  draws the picture and lets the player save it, and the web address is off
  the picture.
- **Neither build calls anything outside itself.** The hall of heroes and the
  save codes are removed rather than left as buttons that fail — CrazyGames
  reject games with buttons that do nothing.
- **One ad break, at the one natural pause:** the player has finished a
  fight, been to the merchant, and asked for the next monster. Never
  mid-turn, never between two rolls, never on a menu button.
- **Poki carries no monster clips.** They ask for a small build; the still
  art already stands in, and an empty clip list means the package never even
  asks for them, so there are no 404s for a reviewer to find.

## A note on the two portal folders

`dev/portal/` is the card game's packaging and this is the dice game's. The
two games are submitted separately and can diverge, so each carries its own
build and its own shim. `shim.js` and `encvid.py` are the same in both today:
if that ever becomes a maintenance problem, share them — but not before, and
not at the cost of one game's package being able to break the other's.
