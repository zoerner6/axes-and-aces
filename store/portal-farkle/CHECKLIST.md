# Monster Farkle on CrazyGames and Poki — what to do

Everything is built and checked. Nothing has been submitted; that part is
yours. Work down this list.

The two packages are **not in git** — they are 200MB and 54MB of build
output. Step 1 makes them. Everything else is uploading and typing.

---

## 1. Make the two packages

Open a terminal in the project folder and run these in order. The first one
takes about twenty minutes; the rest take a minute or two.

```bash
python dev/portal/farkle/encvid.py --out .vid-small
```

```bash
python dev/portal/farkle/build.py crazygames --vid .vid-small --zip
```

```bash
python dev/portal/farkle/build.py poki --zip
```

You now have:

- `dist/monster-farkle-crazygames.zip` — 200.9 MB
- `dist/monster-farkle-poki.zip` — 54.3 MB

## 2. Prove they work before you upload

```bash
node dev/portal/farkle/check.cjs crazygames
```

```bash
node dev/portal/farkle/check.cjs poki
```

CrazyGames prints 27 checks and Poki 26. Each must end with **All ... checks
pass.** If anything fails, do not upload: the message says what broke.

---

## 3. CrazyGames

1. Sign in at **developer.crazygames.com**.
2. **Add a new game.** Name it `Monster Farkle`.
3. Upload `dist/monster-farkle-crazygames.zip`.
4. Covers — upload all three from `store/portal-farkle/`:
   - `crazygames-cover-landscape-1920x1080.jpg`
   - `crazygames-cover-portrait-800x1200.jpg`
   - `crazygames-cover-square-800x800.jpg`
5. Video: `preview-landscape-1920x1080.mp4`.
6. Screenshots: `screenshot-1-fight.png`, `screenshot-2-boss.png`,
   `screenshot-3-scoring.png`.
7. Description, controls, tags: copy them from `SUBMISSION.md`.
8. Submit for review.

**If they ask about ads:** one midgame break, between fights, never during a
turn. No rewarded ads and no banners — CrazyGames turn monetization off
during Basic Launch anyway. The death screen is the obvious home for a
rewarded ad once they invite you to Full Launch.

## 4. Poki

1. Sign in at **developers.poki.com**.
2. **New game.** Name it `Monster Farkle`.
3. Upload `dist/monster-farkle-poki.zip`.
4. Thumbnail: `poki-thumbnail-square-1024x1024.jpg`.
5. Video: `preview-portrait-1080x1620.mp4`.
6. Screenshots: the two `screenshot-phone-*.png` files.
7. Description and tags: `SUBMISSION.md`.
8. Submit.

**Read `PORTAL-NOTES.md` before you submit to Poki.** There are two things
there worth knowing first: they may say no on content grounds, and they ask
for web exclusivity by default, which the live site rules out.

---

## 5. If they come back with changes

Change `dev/farkle.html`, not the package. Then rebuild (step 1), re-check
(step 2) and upload again. The package is generated, so anything edited
inside `dist/` is gone the next time it is built.
