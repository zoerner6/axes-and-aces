# Axes & Aces: Handoff

This file is for moving the project from the cloud session to a local Claude Code session on Josh's PC (`C:\dev\axes-and-aces`).

**Read this first, Claude:** Josh is not a developer. Keep replies short and simple, as if explaining to a 12-year-old. Skip code talk and file paths. Do everything you can yourself, and only ask him to do things that truly need him.

---

## 1. What this is

**Axes & Aces** is a free dark comic card adventure: you fight monsters with poker hands.

- **Website:** https://axesandaces.com, hosted on Netlify.
  - `index.html` is the sales front page.
  - `play.html` is the game.
- **Claude preview of the game:** https://claude.ai/artifact/S9jVuJt6v2otf8FDSpmyuT. It's a public artifact, and it runs only the game, not the front page.
- **Android app:** made with Capacitor. It is a thin shell that opens https://axesandaces.com.
  - Website updates reach the app automatically.
  - The app only needs rebuilding for native changes, such as a new version number, icon or permissions.
- **iPhone app:** not started.

## 2. Where things are (repo root)

| Path | What it is |
|---|---|
| `dev/game.html` | **Source of the whole game.** It's one big file containing the HTML, CSS and JS. Edit this one. |
| `dev/landing.html` | **Source of the front page** at axesandaces.com. Edit this one. |
| `dev/build.py` | Turns those two files into the live site files. Run it with `python dev/build.py`. |
| `index.html`, `play.html`, `sw.js` | **Built files.** Don't edit them by hand; run `dev/build.py`. |
| `art/`, `vid/`, `music/` | All pictures (webp), monster videos (mp4) and songs (mp3) used by the site. |
| `b/` | Facebook share pages and pictures, 220 of them (one per monster, achievement, quest and hero look). |
| `img/` | Front-page extra pictures. |
| `BRAND.md` | **Brand brief.** Check every new screen or picture against it. |
| `privacy.html` | Privacy policy. Its email is support@axesandaces.com. |
| `netlify.toml` | Netlify settings: no-cache headers for the HTML pages and a block on `/store/*`. |
| `netlify/functions/` | Leaderboard and cloud-save server code. The database link is only in Netlify's secret `DATABASE_URL`. |
| `store/google-play/` | Google Play upload files: the aab, listing text, screenshots, feature graphic and icon. |
| `dev/android-app/` | Android app project (Capacitor). |
| `dev/gen/` | Old helper scripts from the cloud session (see section 7). |
| `dev/tests/` | Browser test scripts (Playwright) used to screenshot and check layouts. |
| `dev/tog.js` | Makes the Facebook share pictures in `b/`. |

## 3. How to make a change and publish it

1. Edit `dev/game.html` (the game) or `dev/landing.html` (the front page).
2. Run `python dev/build.py`.
3. Test locally: run `python -m http.server 8000` in the repo root, then open http://localhost:8000. Check it on a phone size too.
4. Commit and push to `main`.
5. **Publish:** `npx netlify deploy --build --prod`.
   - The Netlify login is already set up on Josh's PC.
   - Keep it to about **one publish per day**, which was Josh's rule. Batch changes together.
6. Tell Josh to open axesandaces.com in a **private window**, so he doesn't see the old cached copy.

When the game changes, also update the Claude preview artifact (section 1 link). It is the game only: the page head skeleton plus `dev/game.html`, published as `index.html`. Its art, vid and music files are already uploaded there.

## 4. Status right now (Oct 31, 2026)

**Waiting on Josh / not live yet:**
- [ ] **Netlify publish.** The new front page, the hero-slot phone fix, the easier monsters and the Facebook-picture fixes are all pushed to GitHub but **not live yet**. Run the publish command in step 3.5. Then check that https://axesandaces.com contains "Play one hand" and that https://axesandaces.com/play.html loads the game.
- [ ] **Google Play.** Upload `store/google-play/axes-and-aces-1.0.aab` (versionCode 2, minSdk 24) in Play Console. Google rejected the first one because it used minSdk 22. Listing text and form answers are in `store/google-play/store-listing.txt`.
- [ ] **App Store (iPhone).** Not started. The front page shows "Coming soon" buttons for both stores.
- [ ] **support@axesandaces.com.** Email forwarding was planned through Porkbun (the domain registrar) but never confirmed as set up.

**Done today:**
- Facebook share pictures:
  - Reworded the share text (no more "Can you beat it too?").
  - Replaced the yellow box with outlined lettering.
  - Each monster now has its own picture (`b/boss_<monster>.jpg`).
  - Level-up and "best run" pictures match the hero's armor (`b/level_t0..5`, `b/fallen_t0..5`).
- Bigger monster intro and merchant "A deal is struck" popups on short laptop screens, and a compact receipt.
- Easier monsters:
  - Monster armor lowered by about a third.
  - Pub (first area) monsters have no armor and 20% less health and attack.
- Android bundle rebuilt: minSdk 24, versionCode 2, same upload key.
- New front page:
  - A rotating hero video reel of boss attacks, with embers.
  - Story comic panels.
  - "Try a hand" vs the dragon with tip popups.
  - A scroll ambush: the werewolf hits you for a critical blow.
  - Strike back: kill the Troll King with a royal flush.
  - Monster videos, 10 quest cards, the hero growth line and feature cards.
  - "Coming soon" app buttons.
- The game moved to `play.html`. The front page forwards straight into the game for:
  - challenge links (`?c=`)
  - Continue links (`?slot=1..3`)
  - the installed app and the Android app
- Phone layout fix for "Choose your hero" slot rows.

## 5. Android app

- Project: `dev/android-app/`.
  - App id `io.github.zoerner6.axesandaces`.
  - It loads `https://axesandaces.com/`, and the front page forwards the app into the game.
- **Signing:** you need Josh's **upload key**, `axes-and-aces-upload.jks`, and its password from `upload-key-password.txt`. Josh got a private copy earlier.
  - **Never commit, upload or print them.**
  - To sign, create `dev/android-app/android/keystore.properties` (it is gitignored):
    ```
    storeFile=C:/path/to/axes-and-aces-upload.jks
    password=THE_PASSWORD
    ```
  - If the key is lost, Google Play's "upload key reset" is the only fix.
- **Build:** run `npm install` in `dev/android-app`, then in `dev/android-app/android` run `gradlew bundleRelease`.
  - Output: `android/app/build/outputs/bundle/release/app-release.aab`.
  - Copy it to `store/google-play/axes-and-aces-1.0.aab`.
  - You need Android SDK 36 and Java 17+.
- **Every new upload needs a higher `versionCode`** in `android/app/build.gradle`. It's 2 now.
- minSdk is set in `android/variables.gradle` (24).

## 6. Game facts worth knowing

These are all in `dev/game.html`.

- **Saves:**
  - 3 hero slots in browser storage: keys `aa_save_N`, `aa_saved_N`, `aa_checkpoint_N`, `aa_name_N` and `aa_slot`.
  - `migrateSaves()` upgrades old saves.
  - Hero names are custom; `nm()` swaps "Edward" for the player's name.
- **Difficulty:**
  - Monster HP comes from `monsterHP(L)`. Monster attack is ×1.25.
  - Monster armor: `foeArmorFor(L, boss) = round((5 + 6.5*(L-1)) * (boss ? 1.5 : 1) / 5) * 5`. That's 5 at level 1 and 30 at level 5.
  - Damage after armor: `armored(dmg, d) = max(ceil(dmg/2), dmg - armor)`.
  - Pub monsters (world 1, area 1) get `pub` softening in `genMonster`: no armor, 0.8× health, 0.8× attack.
  - Player armor blocks at most 50% of a hit (25% on critical blows).
  - Ace Bonus: a flat +10 per Ace.
- **Layouts:**
  - Phone: stacked.
  - Mid desktop: 900–1259px wide.
  - Full-screen desktop: 1260px+ with a 5:4 or wider aspect ratio.
  - Short desktop screens shrink popups, with media queries on `max-height` 900 and 700.
- **Rules from Josh:**
  - No popup should need scrolling.
  - No text on top of text.
  - No cropped heads.
  - No emoji.
  - Always write the address as "AxesAndAces.com".
- **Music:** one song per world (`music/w1..w10.mp3`), plus `boss.mp3` and the fight songs `fight1`/`fight2`.
- **Share links:** `b/<key>.html` are the Facebook preview pages; they forward to the site.
  - Keys: `ach_*`, `quest1-10`, `boss_<monster>`, `level_t0-5`, `fallen_t0-5`, `daily`, `game`.
  - Old keys (`boss`, `level`, `fallen`) are kept so already-posted links still work.

## 7. Making new art, videos and share pictures (advanced)

- **Images and videos** were made with the Kie.ai API:
  - images: nano-banana-2
  - video: seedance-2-mini 720p
  - music: Suno V4_5
- It needs the `KIE_API_KEY` environment variable. That key was a secret in the cloud environment, so Josh would need to add it to his PC.
- About 2,267 Kie credits were left. ElevenLabs voice never worked.
- **Cutouts:** rembg `isnet-general-use`, then PIL to webp.
- The scripts in `dev/gen/` (kie.py, vid*.py, cut*.py, music*.py, bragpages.py, deploy.sh and others) **still contain the cloud session's folder paths** (`/tmp/claude-0/...scratchpad`). Update the paths before reusing them.
- `dev/gen/deploy.sh` was the cloud publish step; locally, use section 3 instead.
- **Facebook share pictures:** `dev/tog.js` draws them with the game's own `bragCard()`.
  1. Serve the repo locally.
  2. Make a copy of `play.html` that exposes `window.__A = {ev: s => eval(s)}` just before the `/* someone shared a challenge link with us */` line.
  3. Run `node dev/tog.js` with its URL and paths updated.
  4. Then run `bragpages.py` to write `b/*.html`.

## 8. Safety rules

- Never commit, print or upload the Android upload key or its password.
- The database link lives only in Netlify's secret `DATABASE_URL`. Never put it in browser code.
- Don't put Josh's personal email on public pages; use support@axesandaces.com.
- Store files must stay unreachable on the website (`/store/*` is blocked in `netlify.toml`).
- Don't add AI model names to commits or code.
