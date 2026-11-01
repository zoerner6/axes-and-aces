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
- **iPhone app:** Capacitor as well, but **not** a website shell. It carries the
  game inside the app and plays with no signal, because Apple turns down apps
  that are only a window onto a website (review guideline 4.2). The monster
  clips are 585MB, far too much to ship, so those still stream from the site
  when there is a connection and the game falls back to the still art when
  there isn't.
  - It is built on a Mac at GitHub, so no Mac is needed here. See section 5b.
  - Because the app's page is served from inside the app and not from the site,
    the videos, the leaderboard and the cloud saves need the full address.
    `REMOTE` in `dev/game.html` adds it. On the website it is empty.

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
| `dev/android-app/` | Android app project (Capacitor). **The iPhone project lives in here too**, at `dev/android-app/ios/`, because both share one Capacitor project. |
| `.github/workflows/ios.yml` | Builds the iPhone app on a Mac at GitHub. See section 5b. |
| `dev/gen/harness.py` | Builds a test page the same way `build.py` builds the real one. Use it for any phone measuring. |
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

## 4. Status right now (Nov 1, 2026)

**Waiting on Josh:**
- [ ] **The app record in App Store Connect.** The iPhone app cannot be sent to
  Apple until the app exists there with bundle ID
  `io.github.zoerner6.axesandaces`. Only Josh can make it. Everything else is
  ready: the three API secrets are stored in the repo and the app compiles.
- [ ] **support@axesandaces.com.** Forwarding at Porkbun. The Porkbun API has
  no endpoint for email forwarding, so it has to be set on the Porkbun website.
  The address is printed on `privacy.html`, which Apple's reviewer will click.
- [ ] **One more publish needed.** The server functions now answer a
  cross-origin call, which the iPhone app needs for the leaderboard and cloud
  saves. That is committed but **not published**. Publish before testing the
  iPhone build, or those two things will fail in the app and work on the web.

**Done Nov 1:**
- Phone layout pass over the whole game and the front page, commit `f9bd76d` -
  **published and live**. The fallen screen, cards printing suit on suit, the
  monster clip, header buttons, the level-up rows, the tape, the merchant, and
  the front page's comic captions and picture rows.
- The iPhone app now carries the game, commit `cc91a19`. Not published, not
  sent to Apple yet.
- Google Play: Josh says the submission is in. Nobody here can see the Play
  Console, so that is his word and not checked.
- Two things given up on purpose on phones: Old Bram's line after you die is
  hidden (it cost about 70px and pushed Start over off the screen), and the
  potion rings are 30px instead of 34 on a 568px-tall screen.

**Known traps:**
- `npx netlify deploy --prod --site axes-and-aces` **fails** with "Not Found".
  The folder is already linked to the site, so leave `--site` off entirely:
  `npx netlify deploy --prod`.
- `dev/game.html` has no `<head>`, so a test page made by injecting into it has
  no viewport meta, and a phone-sized Chrome then lays the page out at 980px
  with every `max-width` rule switched off. Build test pages with
  `python dev/gen/harness.py`, and check `matchMedia('(max-width:560px)')`
  is true at 320 wide before trusting any measurement.
- The whole repo root is published, so `HANDOFF.md`, `BRAND.md` and `dev/` are
  readable on the live site. The repo is public on GitHub anyway, so nothing is
  exposed that wasn't already, but it is untidy.

**Done Oct 31:**
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

## 5b. iPhone app

- Same Capacitor project as Android, at `dev/android-app/ios/`. App id
  `io.github.zoerner6.axesandaces`, the same one Android uses.
- **No Mac needed.** It builds on a Mac at GitHub. Open the repo's **Actions**
  tab, pick **iPhone app**, press **Run workflow**. Leaving "Send the build to
  TestFlight" off only checks that it compiles; turning it on signs it and
  sends it to Apple.
- **It is not a website shell.** Unlike Android, the iPhone build carries the
  game inside the app, because Apple turns down apps that are only a window
  onto a website. The workflow does that itself, every build:
  1. runs `dev/build.py`,
  2. copies `play.html` in as the app's `index.html`, plus `art/`, `img/`,
     `icons/`, `music/` and `manifest.json`,
  3. drops the `server.url` line from `capacitor.config.json`, so the app runs
     off its own copy.
  None of that copy is committed - it is assembled on the runner and
  gitignored here. **Android is untouched by this** and still loads the
  website, so site updates keep reaching the Android app without a rebuild.
- **The monster clips are not in the app.** 585MB is far too much to ship, so
  they stream from the site when there is a connection. With no signal the
  game falls back to the still art, which it already did whenever a clip
  failed to load.
- **Three secrets must exist** in the repo (Settings > Secrets and variables >
  Actions). All three were added 2026-10-31 and are in place:
  `APPSTORE_ISSUER_ID`, `APPSTORE_KEY_ID`, `APPSTORE_P8`. Apple only lets the
  `.p8` file be downloaded once, so Josh needs his own copy kept safe.
- **The app must exist in App Store Connect first**, with that same bundle ID.
  That is the one step nobody here can do.
- **Version numbers** are in `ios/App/App.xcodeproj/project.pbxproj`:
  `MARKETING_VERSION` is the public version (1.0), `CURRENT_PROJECT_VERSION` is
  the build number and **must go up on every upload**. It is 1 now, so the
  first upload is fine and the second needs a bump.
- **If Apple still rejects it under guideline 4.2**, the answer is not to argue:
  it means something still looks like a web page. Check that the build really
  did drop `server.url` (the step prints the config) and that the app opened
  its own files rather than the site.

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
