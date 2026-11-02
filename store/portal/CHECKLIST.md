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

Then this, which takes under a minute:

```bash
python dev/portal/build_portal.py crazygames --vid .vid-small --zip
```

That writes the folder `dist/crazygames`, which is what you upload, and a zip
beside it for keeping or sending. It should print about 200 MB and 1,022 files.
If it prints over 250 MB or over 1,500 files, stop and say so.

### 2. Make an account

Go to **developer.crazygames.com** and sign up. It is free.

### 3. Start a new game submission

Click **Submit a game**. It opens on six things to confirm about the game. Those
are yours to tick, not mine. Three are plain fact and three are your judgment:

| They ask | Where it stands |
|---|---|
| Loads in desktop Chrome within 20 seconds, no errors | Yes. About 6 MB loads before the first fight, and a 68-screen sweep found no errors. |
| Works on mobile, or is marked desktop only | Yes. Checked at 390x844, 375x667, 360x740 and 320x568. |
| Default language is English | Yes. |
| The first minute makes it clear what to do | Your call. It opens in the story rather than a menu. |
| Someone other than you has played it start to finish | Your call. |
| You own the code, art and sound | Your call. |

**Continue** stays greyed out until all six are ticked. The next screen asks:

- **Game name** - Axes & Aces
- **Game engine** - HTML5. Not "Externally hosted (iframe)": that one points at
  axesandaces.com, and the whole point is that the package carries its own files.
- **Does your game save progress?** - **Yes, using the Data Module from the
  CrazyGames SDK.** There are four answers and this is the only one that matches
  the build. Their own documentation says the data module stays switched off
  unless this answer names it, so any other choice here loses every save.
- **Mobile orientation** - this appears once you tick mobile. **BOTH.** The game
  plays upright on a phone and wide on a desktop.
- **Game options** - tick *The game supports mobile devices*. Leave the
  multiplayer and audio-muting boxes alone: the game is single-player and it
  handles its own sound during an ad.

### 4. Upload the folder, not the zip

**CrazyGames do not accept a zip.** Drop one in and it answers "Archive files are
not supported, please drag and drop the files directly in the upload zone."

Drag the folder `dist/crazygames` onto the upload box, or use its **Select
folder** button and pick that folder. All 1,022 files go up, which takes a while.
It needs to find `index.html` at the top of what you give it, and it does.

The zip is still worth having for sending the build somewhere or keeping a copy.
It is just not what this box wants.

### 4b. The QA step

Pressing **Preview** uploads nothing new - it builds the game on CrazyGames and
opens it in their QA player, with a panel of measurements down the right. Play
until a fight actually starts, because two of their numbers only appear once the
game sends its first gameplay event.

What it measured on 2 November 2026, on their own instrumentation:

| Their number | What came back | Their limit |
|---|---|---|
| Total size | 200.9 MB | 250 MB |
| Load size | 5.4 MB cold, 1.7 MB on a revisit | 50 MB, or 20 MB for the mobile home page |
| Load time | 6.4 seconds | 20 seconds |

Load time is the gap between their Play button and the game's first gameplay
event, so it counts the seconds you spend reading the opening story. Dawdle and
it reads 60 seconds. That is you, not the game.

**Do not close the QA tab when you press Continue.** It opens a second tab and
then hands the results over. Close it too early and you get "Failed to retrieve
QA results" and have to restart the preview.

Then comes a checklist with Yes/No on each row, ending in "I confirm that these
results are correct." Those are yours to mark. Two pass automatically. For the
rest, here is what is actually true of the build:

| Their check | Where it stands |
|---|---|
| Initial download size <50MB | Passes automatically |
| First gameplay start | Passes automatically |
| First gameplay start implemented correctly | It fires when a fight starts, not on the menus. |
| Complies to Gameplay requirements | Your call. |
| Runs on all CrazyGames domains | Nothing in the build is tied to a domain. |
| Browser checks | Ran clean in Chrome. |
| Device checks: Mobile | **Use their Show QR and play it on your phone.** Neither of us has run it on real hardware - only at phone sizes in a desktop browser. |
| No external ads | Nothing but their own SDK. |
| Does not offer external login options | There is no login of any kind. |
| In-game mention of Terms & Conditions and/or Privacy Policy | **The game says neither, anywhere.** It also collects nothing, sends nothing off the page and has no accounts of its own; progress sits in CrazyGames' own storage under their policy. N/A is the honest mark, but read the row and decide. |

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
