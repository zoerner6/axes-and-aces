# Monster Farkle on the portals — what you should know first

Read this before submitting. It is the part that is judgement rather than
upload.

## The two packages, measured

Measured on the finished folders, not estimated.

|  | CrazyGames | Poki |
|---|---|---|
| Files | 1,034 (limit 1,500) | 621 |
| Total size | 201.5 MB (limit 250 MB) | 54.5 MB |
| Zip | 200.9 MB | 54.3 MB |
| Downloaded before the game is playable | **3.5 MB** | 3.5 MB |
| Monster clips | Yes, all 413 | No, the still art stands in |
| Addresses outside the package | 2 — its own portal's SDK, and the hall of heroes | 1 — its own portal's SDK |
| Hall of heroes | Yes, the real one | No, removed |

The 3.5 MB is real: counted over the wire in a browser, from opening the
page to the SDK's own `gameplayStart` firing. CrazyGames cap that at 50 MB
and want it under 20 MB to qualify for their mobile home page, so there is
a lot of room.

CrazyGames' 250 MB ceiling only applies once their SDK is in the build. It
is in.

## Poki may say no, and it will not be for a technical reason

Two things to weigh before you spend time on them:

1. **Content.** Their out-of-scope list names sustained scary themes and
   gambling. This game has skeletons, ghouls and dice. It is not gambling —
   nothing is wagered and no money moves — and `SUBMISSION.md` says so
   plainly on the form. But "dice game with undead" is the kind of thing
   that gets a second look.
2. **Exclusivity.** Poki ask for web exclusivity by default, and
   AxesAndAces.com already hosts the game. Their own fallback for that is a
   one-time flat fee instead of revenue share. Expect that conversation.

CrazyGames have neither problem. If you only want to do one, do CrazyGames.

## The hall of heroes: on for CrazyGames, off for Poki

**CrazyGames carries the real hall of heroes and the real save codes.** They
allow a game to call its own back end, and ours answers one. Checked against
the live site on 2026-11-02:

```bash
curl -i -X OPTIONS https://axesandaces.com/.netlify/functions/get-scores -H "Origin: https://games.crazygames.com"
```

That returns `204` with `access-control-allow-origin: *`, so the call works
from the portal's own domain. `check.cjs` goes further and actually fetches
the board from inside the package, cross-origin, as a last check before you
upload. If it ever stops working the panels say so and the game plays on
regardless — but set `"online": False` for crazygames in
`dev/portal/farkle/build.py` and rebuild, because CrazyGames reject games
with buttons that do nothing.

The older note in this repo said those functions answered `405` and had to
stay off. That was true before the site was published on 1 November; it is
not true now. Run the curl rather than believing either version.

**Poki has it off**, and that is their rule: no external calls until
approved. Both the hall and the save codes are removed from that build
rather than left as buttons that fail.

## The ad break

One midgame break, at one place: the player has finished a fight, been to
the merchant, and tapped Onward for the next monster. Never mid-turn, never
between two rolls, never on a menu button.

- CrazyGames: rate-limited here to their one-every-three-minutes cap, and
  the first two fights are free of it so a new player gets started.
- Poki: they time their own breaks, so the game never second-guesses them.
  The first fight is free of it.

No rewarded ads and no banners, on purpose. CrazyGames turn monetization
off during Basic Launch. The death screen is the obvious home for a
rewarded ad — "get back up" — once they invite you to Full Launch.

If an ad fails to fill, is blocked, or hangs, the game carries on: every
path through the break ends by resuming play, and there is a 45-second
backstop so a stuck ad can never strand a player. That is checked rather
than assumed — `check.cjs` runs the break with no SDK reachable and proves
the game comes back.

## A bug this work found and fixed

`clearPanelTimers()` in `dev/farkle.html` was defined and never called. It
was meant to stop one screen's typing landing in the screen that replaced
it — the fix for a monster blocking your path announcing that it had not
seen you. The function was there, so a check that looked for it passed; the
call was not, so the bug was still live on the site.

It is wired in now, and `check.cjs` asserts the behavior instead of the
text: it starts a fight intro, replaces the panel underneath it, waits past
both timers and checks that nothing stale arrived.

**This is on the live site too**, and will go out with the next site build.

## What was not done here

Nothing was published to Netlify and nothing was submitted to either
portal. The packages are built and checked; the uploading is yours.
