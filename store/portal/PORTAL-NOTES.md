# Axes & Aces on the games portals — what was built and what to watch

Written 2026-11-01. Rules checked against the live docs the same day.

---

## The short version

**CrazyGames: ready to submit.** The game fits their limits with room to spare,
the monsters keep their video, and everything they forbid has been taken out.

**Poki: ready to submit, but they may say no, and not because of anything
technical.** Poki is a hand-picked platform aimed at an audience that includes
children. Their published list of what is out of scope names "graphic violence,
including open or infected wounds and visible body fluids", "sustained scary
themes", and "gambling". Axes & Aces has skeletal ghouls, blood, death, and a
poker engine. Poker is not named either way in their rules.

That is a judgment call only Poki can make. The package is built and the text is
written, so submitting costs a form and a wait. But do not count on it, and do
not start rewriting the game for them before they have seen it.

There is a second Poki catch that is about money, not content: **they ask for web
exclusivity by default.** The game is live at axesandaces.com, so the exclusive
deal does not fit as things stand. Their own answer for that case is a one-time
flat license fee with no revenue share. Their form asks outright whether the game
is out already. Say yes.

---

## What the portals actually allow

Checked at `docs.crazygames.com` and `developers.poki.com` on 2026-11-01.

| | CrazyGames | Poki |
|---|---|---|
| How you submit | Upload at developer.crazygames.com | Pitch form, then they decide |
| Total size | 250 MB with their SDK (50 MB without) | No published limit |
| File count | 1,500 | No published limit |
| First playable download | 50 MB, or 20 MB to be shown on their mobile home page | No number; they say players leave after 10 seconds |
| Their SDK | Optional at Basic Launch, required at Full Launch | Required |
| Other ad code | Forbidden | Forbidden |
| Your own backend | Allowed | Blocked until you ask them to allow it |
| Links off the page | Only community links on the menu | Only through their own `openExternalLink` |
| Money of your own | Invite only, via them | Not allowed at all |

### CrazyGames runs in two stages

1. **Basic Launch.** The game goes live to a limited audience for 7 to 21 days.
   Ads are off, even if the ad code is in. It ends once the game has been live 7
   days *and* hit 500 plays, or automatically at 21 days.
2. **Full Launch.** If the playtime, conversion and retention numbers clear their
   bar, they invite you up and monetization turns on.

The SDK is in the build already. It is optional at this stage, but putting it in
is what raises the size allowance from 50 MB to 250 MB — which is the only reason
the monster videos could come along.

---

## The packages

Measured on the finished folders, not estimated.

| | CrazyGames | Poki |
|---|---|---|
| Files | 1,022 (limit 1,500) | 609 |
| Total size | 200.9 MB (limit 250 MB) | 53.9 MB |
| Downloaded before the first fight | **5.4 MB** | about 3 MB |
| Monster videos | Yes, all 413 clips | No |
| Leaderboard and cloud save | No, see below | No |

The 5.4 MB figure is the real thing: measured in a browser, counting every byte
that crossed the wire between opening the page and the SDK's `gameplay start`
firing. The cap is 50 MB and the mobile-home-page bar is 20 MB, so the game
clears both comfortably. The page itself loads in well under a second.

### The videos came back

The original clips are 413 files and 583 MB, which no portal would take. They are
1280x720 at about 1.7 Mbps, which is far more than the monster box ever shows.
Re-encoded (idle clips at 854 wide, attack clips at 768, scenes at 854) they come
to **147 MB** — a quarter of the size, and side by side the difference is hard to
see. That fits inside the 250 MB allowance with 50 MB to spare, so every monster
still moves and strikes on CrazyGames.

They are left out of the Poki build on purpose. Poki publish no size limit but
make a point of small builds and fast loading, and they are the stricter reviewer.
The game already handles a missing clip by showing the still art instead, so
nothing breaks. If Poki say the videos are fine, it is one word in
`dev/portal/build_portal.py` (`"video": False` becomes `True`) and a rebuild.

---

## What changed in the game, and why

None of this touches the live site. `dev/build.py` and everything it produces are
untouched; the portal packages are built separately by `dev/portal/build_portal.py`
from the same `dev/game.html`.

- **The fonts now travel with the game.** Both portals forbid calling a font CDN
  at run time, and Poki name Google Fonts specifically. Seven font files, 164 KB.
  This also fixed a real bug: the game used to throw errors on every screen when
  Google Fonts could not be reached. It no longer does.
- **It starts in the game.** A first-time player used to get a hero-slot menu,
  then a name box, then the story. Now they land straight in the opening scene
  with a hero called Edward. Someone who has played before still picks their hero.
- **Nothing links off the page.** The Facebook button, the copy-link button and
  the web address printed on the share picture are all gone. The share panel now
  just makes a picture you can save, and says so.
- **"Brag" is now "Poster".** The old button was Facebook blue and promised
  sharing the build no longer does.
- **The splash logo over the hero list is gone.** Poki ask for splash screens to
  be removed, and without it the panel fits a short phone without scrolling,
  which it did not before.
- **The portals are told when play starts and stops**, so their own measurements
  work, and there is one ad break: the moment the player leaves one fight and
  asks for the next. Never inside a hand, never on a menu button. That is the
  only spot both portals allow.
- **Neither build calls anything outside itself.** The leaderboard, the cloud
  save and the score posting are taken out rather than left as buttons that fail.
  The Poki build also no longer asks for video files it does not carry.

Each package now contains exactly one address pointing off the page: its own
portal's SDK. Progress is saved in the browser, as it is on the site.

### Why the leaderboard is off even on CrazyGames

CrazyGames do allow a game to call its own back end, so the plan was to keep it.
Then I tested the real thing. The functions deployed at axesandaces.com answer a
preflight with `405 Use POST` and send no allow-origin header at all, so every
call from another domain fails before it starts.

The code to fix that is already in `netlify/functions/_db.mjs` — it sets the
headers and answers `OPTIONS` properly. It has just never been published, so the
live functions are older than the repository.

Shipping a leaderboard button that always fails, and throws on every screen while
doing it, is a rejection on its own: CrazyGames reject games with buttons that do
nothing. So both builds are self-contained for now.

**To turn it back on:** publish the site once (that alone fixes the live
functions), then set `"online": True` for crazygames in
`dev/portal/build_portal.py` and rebuild. Check it first with:

```bash
curl -i -X OPTIONS https://axesandaces.com/.netlify/functions/save-game -H "Origin: https://games.crazygames.com" -H "Access-Control-Request-Method: POST"
```

A `204` with an `access-control-allow-origin` header means it is ready. A `405`
means the publish has not happened yet.

---

## One bug found and fixed along the way

The Grimstone Dragon — the boss at the end of the first quest — introduced itself
with the line "It guards the way to Anna. undefined". Every other boss has a suit
it shrugs off and the dragon does not, so the game was printing an empty slot.

This was in the game already, not something the portal work caused, which means
it has been showing on axesandaces.com too. It is fixed at the source
(`dev/game.html`), so the next time the site is built it goes away there as well.
It is worth pushing: "Buggy or broken gameplay" is on Poki's own list of reasons
they turn a game down, and this was on the most important screen of the first
quest.

## Things left undone on purpose

- **No rewarded ads.** The death screen is the obvious home for one, but
  CrazyGames turn monetization off during Basic Launch and reject games with
  reward buttons that do nothing. Add it when they invite you to Full Launch.
- **No banners.** Same reason.
- **No Poki backend.** If Poki accept the game and you want the leaderboard,
  they allow it after a request under Settings → CSP on their dashboard.

## Things to keep an eye on

- The game's hand-guide and shop panels scroll on a short phone. They did before
  this work too, and they are inside a panel, not the page. Worth tidying one
  day; not a blocker for either portal.
- CrazyGames test in an iframe at ten different sizes, down to 800x450. The game
  was checked at 390x844, 375x667, 360x740 and 320x568 and has no page scroll,
  no cropped art and no clipped text at any of them.
- If you ever turn the Netlify functions off, the CrazyGames build still plays;
  the leaderboard panel just says it is not available.
