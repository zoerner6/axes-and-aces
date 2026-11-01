# What to click and upload

Two things to put the game on. Do CrazyGames first — it is a straight upload and
they take almost everyone at the first stage. Poki is a pitch and a wait.

Everything you need is in the folder `store/portal` except the two game packages,
which are too big for the repository. Rebuild them with one command (step 1).

---

## Part 1 — CrazyGames

### 1. Build the package

Open a terminal in the project folder and run this. It takes about ten minutes
the first time, because it shrinks all 413 monster videos.

```bash
python dev/portal/encvid.py --out .vid-small
```

Then this, which takes under a minute and makes the zip:

```bash
python dev/portal/build_portal.py crazygames --vid .vid-small --zip
```

You now have `dist/axes-and-aces-crazygames.zip`. It should be about 190 MB.
If the numbers it prints are over 250 MB or over 1,500 files, stop and say so.

### 2. Make an account

Go to **developer.crazygames.com** and sign up. It is free.

### 3. Start a new game submission

Click **Submit a game**. Choose HTML5 when it asks what the game is built with.

### 4. Upload the zip

Upload `dist/axes-and-aces-crazygames.zip`. Their tool unpacks it and runs its own
checks. It should find `index.html` on its own.

### 5. Fill in the text

Open `SUBMISSION.md` in this folder and copy each block across:

- Title
- Short description
- Long description
- Controls (they may call it instructions)
- Tags

### 6. Upload the three covers

From this folder:

| They ask for | Upload this file |
|---|---|
| Landscape, 16:9 | `crazygames-cover-landscape-1920x1080.jpg` |
| Portrait, 2:3 | `crazygames-cover-portrait-800x1200.jpg` |
| Square, 1:1 | `crazygames-cover-square-800x800.jpg` |

### 7. Upload the two preview videos

Both are required.

| They ask for | Upload this file |
|---|---|
| Landscape preview | `preview-landscape-1920x1080.mp4` |
| Portrait preview | `preview-portrait-1080x1620.mp4` |

They are 19 seconds each and silent, which is what they ask for.

### 8. Send it

Submit. They review by hand. The game goes into **Basic Launch**: live to a
limited audience, with ads switched off, for between 7 and 21 days.

### 9. What happens next

Basic Launch ends once the game has been live 7 days **and** reached 500 plays,
or automatically after 21 days. If the playtime and the number of people who come
back are good enough, they invite you to **Full Launch** and turn the money on.

**When that invitation arrives, come back to me.** Full Launch needs a few more
things added — a rewarded ad on the death screen, their save system, and their
mute control. None of it is in yet on purpose, because they reject games that
show ad buttons while ads are switched off.

---

## Part 2 — Poki

Read `PORTAL-NOTES.md` first. The short version: Poki pick games by hand for an
audience that includes children, and their rules name blood, scary themes and
gambling as out of scope. This game has blood, skeletons and poker. They may well
say no, and that will be about the content, not the build.

It costs you a form and a wait, so it is still worth doing.

### 1. Build the package

```bash
python dev/portal/build_portal.py poki --zip
```

You get `dist/axes-and-aces-poki.zip`, about 50 MB. You do not upload this yet —
Poki want a link they can play first.

### 2. Put a copy somewhere they can play it

They ask for "a browser build we can access without a login". The simplest way is
a Netlify draft, which does not count against the daily publish limit:

```bash
npx netlify deploy --dir dist/poki --site axesandaces
```

That prints a draft URL. Copy it. Check it opens and plays before you go on.

### 3. Fill in their form

Go to **developers.poki.com/guide/share**. Copy the answers from `SUBMISSION.md`:

- Your name, email, studio name
- Team size: Just me
- Game title: Axes & Aces
- Describe your game in a few sentences
- Engine: **Custom engine / framework**
- Build link: the draft URL from step 2
- Three screenshots: `screenshot-1-fight.png`, `screenshot-2-boss.png`,
  `screenshot-3-reward.png`
- Why it is a good fit
- **Has this game already been released on other platforms? Answer Yes.**

### 4. Answer Yes about the other platforms, and mean it

The game is live at axesandaces.com. Poki ask for web exclusivity by default, so
if they are interested they will offer a one-time fee instead of a revenue share.
Hiding it would cost you the deal later. Say yes.

### 5. Wait

They do a content check, then playtests, then a final review that takes one to
two weeks. If they take it, the whole run to being live is two to three months.

---

## If something looks wrong

- **The build command stops with "Patch failed".** That means the game's source
  moved since this was written. It is deliberate: it stops rather than quietly
  shipping something broken. Send me the message it printed.
- **CrazyGames says the game is too big.** Check the numbers the build printed.
  The limits are 250 MB and 1,500 files.
- **Either portal rejects it.** Send me exactly what they said.

## What this did not touch

axesandaces.com is unchanged. These packages are extra files built from the same
source; nothing about the live site, the way it is built, or the way it is
published has changed.
