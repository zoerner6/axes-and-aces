"""Build a games-portal package of Monster Farkle from dev/farkle.html.

The live site is built by dev/build.py and is not touched here. This writes a
separate, self-contained folder per portal: its own index.html, its own fonts,
and only the assets that portal allows.

  python dev/portal/farkle/build.py crazygames --vid <folder of small clips> --zip
  python dev/portal/farkle/build.py poki --zip

Every patch below must match the source exactly once. If dev/farkle.html moves
on under us the build stops instead of quietly shipping a broken game. After
the patches the finished page is scanned for anything still pointing off the
package, because a patch list that all applied is not the same thing as a
package that calls nothing - that has to be asserted about the output.
"""
import argparse, pathlib, re, shutil, zipfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]

PORTALS = {
    "crazygames": {
        "sdk": '<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>',
        "host": "sdk.crazygames.com",
        "ad_gap": 180_000,      # their cap is one midgame ad every three minutes
        "ad_free_fights": 2,    # let a new player get properly started first
        # CrazyGames allow a game to call its own back end, and ours now
        # answers one. Checked on 2026-11-02 against the live site:
        #   curl -i -X OPTIONS https://axesandaces.com/.netlify/functions/get-scores \
        #        -H "Origin: https://games.crazygames.com"
        #   -> 204, access-control-allow-origin: *
        # So the hall of heroes and the save codes work from the portal's own
        # domain. If a call ever fails the panels say so and the game plays on
        # regardless. Set this back to False if that stops being true, and run
        # the curl above before believing either way.
        "online": True,
        "video": True,
    },
    "poki": {
        "sdk": '<script src="https://game-cdn.poki.com/scripts/v2/poki-sdk.js"></script>',
        "host": "game-cdn.poki.com",
        "ad_gap": 0,            # Poki times the breaks itself; never time them here
        "ad_free_fights": 1,
        "online": False,        # Poki blocks every external call until approved
        "video": False,         # they ask for a small build; the still art stands in
    },
}

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Monster Farkle</title>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#14100d">
<meta name="description" content="Monster Farkle: a free dice game. Six dice, one monster. Wind up the blow, or lose the lot.">
{sdk}
<style>html,body{{height:100%}}
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:dark}}
body{{margin:0;font:14px system-ui,sans-serif;background:#14100d;overscroll-behavior:none;
-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}}
img{{max-width:100%}}[hidden]{{display:none!important}}
.ad-playing #app{{visibility:hidden}}
input{{-webkit-user-select:text;user-select:text}}
</style>
<style>{faces}</style>
</head><body>
"""
TAIL = "</body></html>"


class Patcher:
    """Exact-match search and replace that refuses to guess."""

    def __init__(self, text):
        self.text, self.log = text, []

    def sub(self, why, old, new, count=1):
        found = self.text.count(old)
        if found != count:
            raise SystemExit(
                "\nPatch failed: " + why
                + "\n  expected %d match(es), found %d" % (count, found)
                + "\n  looking for: %r\n" % old[:180]
                + "dev/farkle.html has changed. Update dev/portal/farkle/build.py.")
        self.text = self.text.replace(old, new)
        self.log.append(why)

    def sub_re(self, why, pattern, new, count=1):
        """For the one very long generated list, where quoting the whole thing
        would be worse than matching its shape."""
        found = len(re.findall(pattern, self.text))
        if found != count:
            raise SystemExit(
                "\nPatch failed: " + why
                + "\n  expected %d match(es), found %d" % (count, found)
                + "\n  pattern: %s\n" % pattern
                + "dev/farkle.html has changed. Update dev/portal/farkle/build.py.")
        self.text = re.sub(pattern, new.replace("\\", "\\\\"), self.text)
        self.log.append(why)


def shim_for(portal, cfg):
    js = (HERE / "shim.js").read_text(encoding="utf-8")
    return (js.replace("__PORTAL__", portal)
              .replace("__AD_GAP__", str(cfg["ad_gap"]))
              .replace("__AD_FREE_FIGHTS__", str(cfg["ad_free_fights"])))


# dev/farkle.html is a fragment: dev/build.py supplies the head. Everything
# above its <style> is head material, and this build writes its own head, so
# the whole prefix goes and the bundled faces take the font link's place.
HEAD_PREFIX = """<title>Monster Farkle</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Germania+One&family=Alfa+Slab+One&family=Oswald:wght@500;600;700&family=Alegreya+Sans:wght@400;500;700;800&display=swap">
<style>"""

BRAND_LINK = ('    <a class="brand" href="index.html" aria-label="Back to Axes &amp; Aces">'
              '<img src="img/farkle-emblem.webp" width="88" height="88" alt="">'
              '<span class="wide-only">Monster </span>Farkle</a>\n')
BRAND_PLAIN = ('    <div class="brand">'
               '<img src="img/farkle-emblem.webp" width="88" height="88" alt="">'
               '<span class="wide-only">Monster </span>Farkle</div>\n')

MENU_HOME = """      <a class="buy" href="index.html"><img class="ico" src="img/emblem-64.webp" alt="">
        <b>Back to Axes &amp; Aces</b><span>The card game and everything else.</span><span class="cost">Leave</span></a>
"""

MENU_ONLINE = """      <button class="buy" data-act="lb"><img class="ico" src="art/i_chest.webp" alt="">
        <b>Hall of heroes</b><span>How far other players got.</span><span class="cost">Open</span></button>
      <button class="buy" data-act="cloud"><img class="ico" src="art/i_bag.webp" alt="">
        <b>Play on another device</b><span>Your private save code.</span><span class="cost">Open</span></button>
"""

BRAG_PANEL_OLD = """  openPanel(`<div class="eyebrow">Share it</div><h2>Brag about it</h2>
    <div class="brag-img" id="bragImg"><span>Making your picture...</span></div>
    <div class="row"><button class="btn ghost" data-act="bragFb">Facebook</button>
      <button class="btn ghost" data-act="bragShare">Share</button>
      <button class="btn ghost" data-act="bragSave">Save</button></div>
    <button class="btn big" data-act="close">Done</button>`);"""
BRAG_PANEL_NEW = """  openPanel(`<div class="eyebrow">Your moment</div><h2>Make a poster</h2>
    <div class="brag-img" id="bragImg"><span>Making your picture...</span></div>
    <button class="btn big ghost" data-act="bragSave">Save the picture</button>
    <button class="btn big" data-act="close">Done</button>`);"""

WATERMARK = """  x.font = '34px "Germania One", Georgia, serif'; x.lineWidth = 7; x.fillStyle = '#ffd35c';
  x.strokeText('Play free at', 58, 540); x.fillText('Play free at', 58, 540);
  x.font = '64px "Germania One", Georgia, serif'; x.lineWidth = 10; x.fillStyle = '#ffffff';
  x.strokeText('AxesAndAces.com', 56, 600); x.fillText('AxesAndAces.com', 56, 600);
"""

DAILY_POST = """    ${nameRow()}
    <div id="lbList"></div>
    <button class="btn big" data-act="postDaily">Post my score</button>
    <button class="btn big ghost" data-act="brag" data-kind="hit">Brag about it</button>"""

FB_HANDLER = """  if(act === 'bragFb'){
    window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(bragUrl()), '_blank', 'noopener');
    return;
  }
"""


def patch(src, portal, cfg):
    p = Patcher(src)

    # 1. This build writes its own head, and the fonts travel with the package.
    #    Neither portal allows a font CDN at run time, and Poki names Google
    #    Fonts specifically. Without them the game threw on every screen.
    p.sub("write our own head and bundle the fonts", HEAD_PREFIX, "<style>")

    # 2. The portal shim, first thing inside the game's own scope.
    p.sub("insert the portal shim", "<script>\n(() => {\n",
          "<script>\n(() => {\n" + shim_for(portal, cfg) + "\n")

    # 3. Nothing may send the player off the page. The mark in the bar and the
    #    menu row both went to the card game's site; in a package there is no
    #    site to go to, so the mark stays and stops being a link.
    p.sub("the mark in the bar is a mark, not a way out", BRAND_LINK, BRAND_PLAIN)
    p.sub("drop the menu row that leaves the game", MENU_HOME, "")
    p.sub("every file comes from this package, nothing from the old site",
          "const REMOTE = /^https?:$/.test(location.protocol) ? '' : 'https://axesandaces.com/';",
          "const REMOTE = '';   /* a portal package carries all of its own files */")
    p.sub("no address for the picture to point at",
          "const SITE = 'https://axesandaces.com/';",
          "const SITE = '';   /* a portal build links nowhere */")

    # 4. The poster. Sharing carries a link, so the panel just draws the
    #    picture and lets the player keep it - and says so.
    p.sub("the panel makes a picture now, it does not share one",
          BRAG_PANEL_OLD, BRAG_PANEL_NEW)
    p.sub("drop the web address printed on the picture", WATERMARK, "")
    p.sub("delete the Facebook share handler", FB_HANDLER,
          "  /* the Facebook share is not part of a portal build */\n")
    p.sub("delete the share handler that carries a link",
          "  if(act === 'bragShare') return bragShare();\n", "")
    p.sub("say what the button does on the victory screen",
          '<button class="btn big ghost" data-act="brag" data-kind="boss">Brag about this win</button>',
          '<button class="btn big ghost" data-act="brag" data-kind="boss">Make a poster</button>')
    p.sub("say what the button does on the death screen",
          '<button class="btn big ghost" data-act="brag" data-kind="death">Brag about how far you got</button>',
          '<button class="btn big ghost" data-act="brag" data-kind="death">Make a poster</button>')

    # 5. Tell the portal when a fight starts, ends and is interrupted.
    p.sub("report that loading has finished",
          "buildTray();\nplaceDice();\n", "buildTray();\nplaceDice();\nAA.loaded();\n")
    p.sub("report gameplay start",
          "  S.phase = 'fight'; updateMusic();\n  fightIntro();",
          "  S.phase = 'fight'; updateMusic(); AA.start();\n  fightIntro();")
    p.sub("report gameplay stop on a win",
          "function won(){\n  busy = true;\n  const d = S.fight.d;",
          "function won(){\n  AA.stop();\n  busy = true;\n  const d = S.fight.d;")
    p.sub("report gameplay stop on a loss",
          "function lost(){\n  busy = true;",
          "function lost(){\n  AA.stop();\n  busy = true;")
    p.sub("resume gameplay when a panel closes over a live fight",
          "function closePanel(){ $('overlay').hidden=true; }",
          "function closePanel(){ $('overlay').hidden=true;\n"
          "  if(S && S.phase === 'fight' && S.fight) AA.start(); }")

    # 6. The one ad break both portals accept: the player has finished a
    #    fight, been to the merchant and asked for the next monster. Never
    #    mid-turn, never between two rolls, never on a menu button.
    p.sub("ad break on the way to the next fight",
          "  if(act === 'leaveShop'){ closePanel(); S.charmOffer = null; return nextFight(); }",
          "  if(act === 'leaveShop'){ closePanel(); S.charmOffer = null;\n"
          "    return AA.adBreak(() => nextFight()); }")

    # 7. A build without the clips must not ask for them. The game already
    #    falls back to the still art, but an empty list means it never sends
    #    the request at all, so the package makes no 404s for a reviewer.
    if not cfg["video"]:
        p.sub_re("never ask for a monster clip this build does not carry",
                 r"const VIDS = new Set\(\[[^\]]*\]\);",
                 "const VIDS = new Set([]);  /* this build ships no clips */")

    # 8. The hall of heroes and the save codes call axesandaces.com.
    if cfg["online"]:
        # Served from the portal's own domain, a relative path would look for
        # the functions there and never find them, so name the site. If a call
        # fails the panels say so and the game plays on regardless.
        p.sub("reach the real hall of heroes from the portal's domain",
              "const API = REMOTE + '.netlify/functions/';",
              "const API = 'https://axesandaces.com/.netlify/functions/';")
        p.sub("plainer wording when the hall cannot be reached",
              '`<p class="menu-note">The hall is not reachable from here.'
              ' Play at AxesAndAces.com to join it.</p>`',
              '`<p class="menu-note">The hall of heroes is not reachable right now.</p>`')
    else:
        p.sub("stop every call off the page",
              "async function api(path, body){",
              "async function api(path, body){\n"
              "  /* This build is not allowed to call anything outside itself. */\n"
              "  throw new Error('Online play is off in this build');\n"
              "  // eslint-disable-next-line no-unreachable")
        p.sub("take the online rows out of the menu", MENU_ONLINE, "")
        p.sub("take the save-code button off the hero screen",
              '    <button class="btn big ghost" data-act="cloud">Play on another device</button>\n', "")
        p.sub("take posting a daily score off the results screen", DAILY_POST,
              '    <button class="btn big ghost" data-act="brag" data-kind="hit">Make a poster</button>')
        p.sub("plainer wording where the hall used to be",
              '`<p class="menu-note">The hall is not reachable from here.'
              ' Play at AxesAndAces.com to join it.</p>`',
              '`<p class="menu-note">The hall of heroes is not part of this build.</p>`')

    return p


# Things that must not survive into a package, and what they would mean.
FORBIDDEN = [
    ("axesandaces.com", "a link or a call back to the live site"),
    ("fonts.googleapis.com", "a font CDN at run time"),
    ("fonts.gstatic.com", "a font CDN at run time"),
    ("facebook.com", "a share that leaves the page"),
    ('href="index.html"', "a link to a page this package does not have"),
]


API_URL = "https://axesandaces.com/.netlify/functions/"


def audit(page, cfg):
    """A patch list that all applied is not a package that calls nothing. Say
    what is actually in the finished page."""
    bad = []
    # An online build is allowed exactly one mention of the site - the
    # functions it calls - and nothing else. Anything more is a link or a
    # picture pointing back at a site the player cannot reach from here.
    allowed_site = page.count(API_URL) if cfg["online"] else 0
    for needle, why in FORBIDDEN:
        n = page.count(needle)
        if needle == "axesandaces.com":
            if allowed_site != 1 and cfg["online"]:
                bad.append("  the leaderboard address appears %d times, wants 1" % allowed_site)
            n -= allowed_site
        if n > 0:
            bad.append("  %-22s x%-3d %s" % (needle, n, why))
    # www.w3.org is the SVG namespace in an inline data URI. It is an
    # identifier, not an address: nothing ever fetches it.
    ok_hosts = {cfg["host"], "www.w3.org"} | ({"axesandaces.com"} if cfg["online"] else set())
    hosts = sorted({h for h in re.findall(r"https?://([a-z0-9.-]+)", page)})
    outside = [h for h in hosts if h not in ok_hosts]
    if outside:
        bad.append("  addresses outside the package: " + ", ".join(outside))
    # The one fix that was defined and never called. Assert the call, not the
    # definition: the definition being there is what fooled the last check.
    if page.count("clearPanelTimers()") < 1:
        bad.append("  clearPanelTimers() is never called - stale panel timers")
    if "AA.adBreak(" not in page:
        bad.append("  no ad break in the page")
    if bad:
        raise SystemExit("\nThe finished page still carries:\n" + "\n".join(bad) + "\n")
    where = "%s, its own portal's SDK" % cfg["host"]
    if cfg["online"]:
        where += "; axesandaces.com, the hall of heroes"
    print("  outside addresses: %d (%s)" % (1 + (1 if cfg["online"] else 0), where))


def copy_assets(out, cfg, vid_dir):
    for name, src in [("art", ROOT / "art"), ("img", ROOT / "img"),
                      ("icons", ROOT / "icons"), ("music", ROOT / "music"),
                      ("fonts", HERE / "fonts")]:
        shutil.copytree(src, out / name, dirs_exist_ok=True)
    if cfg["video"]:
        if not vid_dir:
            raise SystemExit("This portal carries the monster clips: pass --vid <folder>.\n"
                             "Make them with: python dev/portal/farkle/encvid.py --out .vid-small")
        src = pathlib.Path(vid_dir)
        if not src.is_dir():
            raise SystemExit("--vid folder not found: %s" % src)
        shutil.copytree(src, out / "vid", dirs_exist_ok=True)


# dev/portal/farkle/harness.py drops a copy of the page with an eval hook in it
# next to the real one so the screen sweep can drive the game. It must never
# reach a portal, so it is left out of the measurements and the zip.
NOT_SHIPPED = {"portaltest.html"}


def measure(out):
    by = {}
    files = [p for p in out.rglob("*") if p.is_file() and p.name not in NOT_SHIPPED]
    for f in files:
        parts = f.relative_to(out).parts
        key = parts[0] if len(parts) > 1 else "(root)"
        row = by.setdefault(key, [0, 0])
        row[0] += 1
        row[1] += f.stat().st_size
    return files, by, sum(f.stat().st_size for f in files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("portal", choices=sorted(PORTALS))
    ap.add_argument("--vid", help="folder of re-encoded clips (encvid.py)")
    ap.add_argument("--out")
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()

    cfg = PORTALS[a.portal]
    out = pathlib.Path(a.out) if a.out else ROOT / "dist" / ("farkle-" + a.portal)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    src = (ROOT / "dev" / "farkle.html").read_text(encoding="utf-8")
    p = patch(src, a.portal, cfg)
    faces = (HERE / "faces.css").read_text(encoding="utf-8")

    # The fragment opens with its stylesheet, which would otherwise land in
    # the body. That renders, but it leaves a <style> sitting among the
    # game's own elements where anything walking the body trips over it.
    # Put it where it belongs.
    m = re.match(r"\s*<style>(.*?)</style>\s*", p.text, re.S)
    if not m:
        raise SystemExit("The game no longer starts with its <style> block. "
                         "Update dev/portal/farkle/build.py.")
    page = (HEAD.format(sdk=cfg["sdk"], faces=faces)
            .replace("</head>", "<style>%s</style>\n</head>" % m.group(1))
            + p.text[m.end():] + TAIL)
    (out / "index.html").write_text(page, encoding="utf-8", newline="\n")
    copy_assets(out, cfg, a.vid)

    files, by, total = measure(out)
    print("\nMonster Farkle  ->  %s  (%s)" % (out, a.portal))
    for k in sorted(by):
        n, b = by[k]
        print("  %-10s %5d files %8.1f MB" % (k, n, b / 2 ** 20))
    print("  %-10s %5d files %8.1f MB" % ("TOTAL", len(files), total / 2 ** 20))
    print("  patches applied: %d" % len(p.log))
    audit(page, cfg)

    if a.zip:
        z = out.parent / ("monster-farkle-%s.zip" % a.portal)
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for f in sorted(files):
                zf.write(f, f.relative_to(out).as_posix())
        print("  zip        %s  %.1f MB" % (z.name, z.stat().st_size / 2 ** 20))


main()
