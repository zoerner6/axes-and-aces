# dev/portal — building Axes & Aces for the games portals

These scripts make a package per games portal out of `dev/game.html`. They never
touch the live site: `dev/build.py` and everything it writes are left alone, and
the packages land in `dist/`, which git ignores.

## The whole thing, start to finish

```bash
python dev/portal/encvid.py --out .vid-small
python dev/portal/build_portal.py crazygames --vid .vid-small --zip
python dev/portal/build_portal.py poki --zip
```

The first command is the slow one, about ten minutes. The clips only need
re-encoding when `vid/` changes.

## What each script does

| Script | What it is for |
|---|---|
| `encvid.py` | Shrinks the 413 monster and scene clips from 583 MB to about 147 MB, so they fit inside a portal's size limit. `--sample` measures without encoding. |
| `fonts.py` | Downloads the five Google fonts the game uses into `dev/portal/fonts/` and writes `faces.css`. Both portals forbid a font CDN at run time. Already run; only needed again if the fonts change. |
| `build_portal.py` | The build. Reads `dev/game.html`, applies the patches, writes `dist/<portal>/`. |
| `shim.js` | The layer between the game and whichever portal is hosting it. `build_portal.py` drops it into the game and fills in the portal's name and ad timing. It also holds `AA.store`, which the game's saves go through: the CrazyGames data module where that SDK is up, the browser everywhere else. |
| `harness.py` | Adds the eval hook `dev/gen/mobscan.cjs` needs, so a built package can be screen-swept. |
| `covers.py` | The cover pictures, into `store/portal/`. |
| `trailer.cjs` | Films a real playthrough for the preview videos. |
| `preview.py` | Cuts that recording to the length and shape CrazyGames accept. |
| `shots.cjs` | The three gameplay screenshots Poki ask for. |

## Why the game waits before it starts

The game reads which save slot you are on the moment its script runs, and a
portal's data module only answers once that portal's SDK has started. So the
build wraps the game's body in `AABOOT`, a gate in the page that starts the SDK
first and runs the game after. It gives up after five seconds, so a missing or
blocked SDK still starts the game - on the browser's own storage, as on the site.

Two things follow from this. The package ends `});` rather than the `})();`
`dev/game.html` closes with, which `harness.py` has to know about. And the gate
sits inside `<body>`, not the head: the SDK puts elements into the page when it
starts and throws if there is no body yet.

## Adding or changing a portal

`PORTALS` at the top of `build_portal.py` holds one entry per portal: its SDK
script tag, how long to leave between ad breaks, how many fights to leave alone
at the start, whether the game may call its own back end, and whether the clips
come along.

## When a patch fails

Every patch is an exact string match that must hit exactly once. If `dev/game.html`
changes under it, the build stops and names the patch and the text it was looking
for, rather than writing a package with half the changes in it. Fix the string in
`build_portal.py` and run it again.

## Checking a build

```bash
python dev/portal/harness.py dist/crazygames
python -m http.server 8765 --bind 127.0.0.1 --directory dist/crazygames
node dev/gen/mobscan.cjs --sizes 390x844,375x667,360x740,320x568 --out dev/gen/out/cg
```

`mobscan.cjs` looks for `audittest.html` on port 8765, which is why the server is
pointed at the package. Stop that server before rebuilding: on Windows it holds
the folder open and the build cannot clear it.
