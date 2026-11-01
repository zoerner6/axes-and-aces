"""Build a games-portal package from dev/game.html.

The live site is built by dev/build.py and is not touched here. This writes a
separate, self-contained folder per portal: its own index.html, its own fonts,
and only the assets that portal allows.

  python dev/portal/build_portal.py crazygames --vid <folder of small clips> --zip
  python dev/portal/build_portal.py poki --zip

Every patch below must match the source exactly once. If dev/game.html moves on
under us the build stops instead of quietly shipping a broken game.
"""
import argparse, pathlib, re, shutil, zipfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]

PORTALS = {
    "crazygames": {
        "sdk": '<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>',
        "ad_gap": 180_000,      # their cap is one midgame ad every three minutes
        "ad_free_fights": 2,    # let a new player get properly started first
        # CrazyGames do allow a game to call its own back end. The catch is the
        # one deployed at axesandaces.com: its functions answer OPTIONS with a
        # 405 and send no allow-origin header, so every cross-origin call fails.
        # The fix is already in netlify/functions/_db.mjs and simply has not
        # been published yet. Until it is, a leaderboard button here would do
        # nothing and throw on every screen, which is a rejection on its own.
        # Publish the site, then set this to True and rebuild.
        "online": False,
        "video": True,
    },
    "poki": {
        "sdk": '<script src="https://game-cdn.poki.com/scripts/v2/poki-sdk.js"></script>',
        "ad_gap": 0,            # Poki times the breaks itself; never time them here
        "ad_free_fights": 1,
        "online": False,        # Poki blocks every external call until approved
        "video": False,         # they ask for a small build; the still art stands in
    },
}

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#14100d">
<meta name="description" content="Axes &amp; Aces: a free dark comic card adventure. Fight monsters with poker hands.">
{sdk}
<style>html,body{{height:100%}}
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:dark}}
body{{margin:0;font:14px system-ui,sans-serif;background:#14100d;overscroll-behavior:none;
-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}}
img{{max-width:100%}}[hidden]{{display:none!important}}
.ad-playing #app{{visibility:hidden}}
input{{-webkit-user-select:text;user-select:text}}
</style>
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
                + "dev/game.html has changed. Update dev/portal/build_portal.py.")
        self.text = self.text.replace(old, new)
        self.log.append(why)

    def sub_re(self, why, pattern, new, count=1):
        """For the two very long generated lists, where quoting the whole
        thing would be worse than matching its shape."""
        found = len(re.findall(pattern, self.text))
        if found != count:
            raise SystemExit(
                "\nPatch failed: " + why
                + "\n  expected %d match(es), found %d" % (count, found)
                + "\n  pattern: %s\n" % pattern
                + "dev/game.html has changed. Update dev/portal/build_portal.py.")
        self.text = re.sub(pattern, new.replace("\\", "\\\\"), self.text)
        self.log.append(why)


def shim_for(portal, cfg):
    js = (HERE / "shim.js").read_text(encoding="utf-8")
    return (js.replace("__PORTAL__", portal)
              .replace("__AD_GAP__", str(cfg["ad_gap"]))
              .replace("__AD_FREE_FIGHTS__", str(cfg["ad_free_fights"])))


GFONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Germania+One'
    '&family=Eczar:ital,wght@0,700;0,800;1,700;1,800&family=Vollkorn:wght@400;500;600;700;800'
    '&family=Fredoka:wght@500;600;700&family=Oswald:wght@500;600;700&display=swap">'
)

SHARE_ROW = (
    '<button class="btn big brag-fb" data-act="bragFb">Share on Facebook</button>\n'
    '      <button class="btn big ghost" data-act="bragShare">Share picture</button>\n'
    '      <button class="btn big ghost" data-act="bragSave">Save picture</button>\n'
    '      <button class="btn big ghost" data-act="bragCopy">Copy link</button>'
)

WATERMARK = (
    """  x.font='34px "Germania One", Georgia, serif'; x.lineWidth=7; x.fillStyle='#ffd35c';"""
    """ x.strokeText('Play free at',58,540); x.fillText('Play free at',58,540);\n"""
    """  x.font='64px "Germania One", Georgia, serif'; x.lineWidth=10; x.fillStyle='#ffffff';"""
    """ x.strokeText('AxesAndAces.com',56,600); x.fillText('AxesAndAces.com',56,600);\n"""
)

FIRST_RUN = """  if(ch){ challengePanel(ch, anySlots()?'title':'name'); return; }
  /* A portal drops the player straight into the game, so a first-time player
     gets a hero in slot 1 and the opening scene with no menu in the way.
     Anyone who has played here before still picks their hero. */
  if(!anySlots()){
    setSlot(1); try{ localStorage.setItem(SKn('name',1), JSON.stringify('Edward')); }catch(e){}
    canSave=true; newRun(true); S.heroName='Edward'; render(); saveGame(); storyPanel(); return;
  }
  slotsPanel();"""


def patch(src, portal, cfg):
    p = Patcher(src)

    # 1. The fonts travel with the package. Neither portal allows a font CDN
    #    at run time, and Poki names Google Fonts specifically.
    p.sub("bundle the fonts",
          GFONTS, "<style>" + (HERE / "faces.css").read_text(encoding="utf-8") + "</style>")

    # 2. The portal shim, first thing inside the game's own scope.
    p.sub("insert the portal shim", "<script>\n(() => {\n",
          "<script>\n(() => {\n" + shim_for(portal, cfg) + "\n")

    # 3. Nothing may send the player off the page.
    p.sub("drop the buttons that leave the page",
          SHARE_ROW, '<button class="btn big" data-act="bragSave">Save the picture</button>')
    p.sub("drop the web address printed on the picture", WATERMARK, "")
    p.sub_re("delete the Facebook share handler", r"[ \t]*case 'bragFb':.*\n",
             "    /* the Facebook share is not part of a portal build */\n")
    p.sub("every file comes from this package, nothing from the old site",
          "const REMOTE = /^https?:$/.test(location.protocol) ? '' : 'https://axesandaces.com/';",
          "const REMOTE = '';   /* a portal package carries all of its own files */")
    p.sub("no address for the picture to point at",
          "const SITE='https://axesandaces.com/';",
          "const SITE='';   /* a portal build links nowhere */")
    p.sub("the panel makes a picture now, it does not share one",
          '<div class="eyebrow">Share it</div><h2>Brag about it</h2>',
          '<div class="eyebrow">Your moment</div><h2>Make a poster</h2>')
    p.sub("thank the player for the poster, not for sharing",
          "'Thanks for sharing! Free potion'", "'Nice poster. Free potion'")
    p.sub("thank the player for the poster, not for sharing (gold)",
          "'Thanks for sharing! Free gold'", "'Nice poster. Free gold'")
    p.sub("the picture is a poster now, not a Facebook card",
          "/* ---- brag cards: a 1200x630 picture made for Facebook, linking back to the game ---- */",
          "/* ---- posters: a 1200x630 picture of the moment, for the player to keep ---- */")
    p.sub("plainer wording when the leaderboard cannot be reached",
          "`<p class=\"menu-note\">The leaderboard isn't available here."
          " Play at AxesAndAces.com to join it.</p>`",
          "`<p class=\"menu-note\">The leaderboard isn't available right now.</p>`")
    #    With sharing gone, a Facebook-blue button labelled "Brag" promises
    #    something the build no longer does. Recolor it and say what it does:
    #    it draws a picture of the moment that the player can keep.
    p.sub("recolor the share-blue button",
          ".btn.brag-fb{background:#1877f2!important;color:#fff!important}",
          ".btn.brag-fb{background:var(--gold)!important;color:#16100d!important}")
    p.sub("recolor the share-blue button on the achievement popup",
          ".ach-pop button,.ach button{flex:0 0 auto;background:#1877f2;color:#fff;",
          ".ach-pop button,.ach button{flex:0 0 auto;background:#f2b632;color:#16100d;")
    p.sub("rename the share button on the death screen",
          '<button class="btn big brag-fb" data-act="brag" data-kind="death">Challenge a friend</button>',
          '<button class="btn big brag-fb" data-act="brag" data-kind="death">Make a poster</button>')
    p.sub("rename the short share buttons", ">Brag</button>", ">Poster</button>", count=4)
    p.sub("rename the win share button",
          ">Brag about this win</button>", ">Make a poster</button>")
    p.sub("rename the daily share button",
          ">Brag about it</button>", ">Make a poster</button>")

    # 4. Land in the game, not on a menu.
    p.sub("start a new player straight into the story",
          "  if(ch){ challengePanel(ch, anySlots()?'title':'name'); return; }\n  slotsPanel();",
          FIRST_RUN)

    # 5. The big logo over the hero list is a splash, which Poki asks you to
    #    drop and CrazyGames has no room for: the portal page already carries
    #    the game's name. Without it the panel fits a short phone without
    #    scrolling, which it did not before.
    p.sub("drop the splash logo above the hero list",
          '<img class="title-logo" src="img/logo-wide.webp" alt="Axes &amp; Aces">'
          '<div class="cine-scene"><img src="art/sc_start_0.webp" alt=""></div>\n'
          '    <h2>Choose your hero</h2>',
          '<div class="cine-scene"><img src="art/sc_start_0.webp" alt=""></div>\n'
          '    <h2>Choose your hero</h2>')

    # 6. Tell the portal when a fight starts, ends and is interrupted.
    p.sub("report gameplay start",
          "  drawUp(); render();\n  if(enc==='ambush') ambush();\n}",
          "  drawUp(); render(); AA.start();\n  if(enc==='ambush') ambush();\n}")
    p.sub("report gameplay stop on a win",
          "async function victory(){\n  const d=foeDef();",
          "async function victory(){\n  AA.stop();\n  const d=foeDef();")
    p.sub("report gameplay stop on a loss",
          "async function defeat(){\n  await wait(400); busy=false;",
          "async function defeat(){\n  AA.stop();\n  await wait(400); busy=false;")
    p.sub("resume gameplay when a panel closes over a live fight",
          "function closePanel(){ stopVoice(); $('overlay').hidden=true; placeBubble(); }",
          "function closePanel(){ stopVoice(); $('overlay').hidden=true; placeBubble();\n"
          "  if(S && S.phase==='play' && S.fight) AA.start(); }")
    p.sub("report that loading has finished",
          "window.claude?.hot?.ready ? window.claude.hot.ready(start) : start(window.claude?.hot?.data ?? {});",
          "AA.loaded();\nwindow.claude?.hot?.ready ? window.claude.hot.ready(start) : start(window.claude?.hot?.data ?? {});")

    # 6. The one ad break both portals accept: moving into the next fight.
    p.sub("ad break on the way into a fight",
          "    case 'fight': closePanel(); startFight(); break;",
          "    case 'fight': closePanel(); AA.adBreak(()=>startFight()); break;")

    # 7. A build without the clips must not ask for them. The game already
    #    falls back to the still art, but an empty list means it never sends
    #    the request at all, so the package makes no 404s for a reviewer to see.
    if not cfg["video"]:
        p.sub_re("never ask for a monster clip this build does not carry",
                 r"const VIDS = new Set\(\[[^\]]*\]\);",
                 "const VIDS = new Set([]);  /* this build ships no clips */")
        p.sub_re("never ask for a scene clip this build does not carry",
                 r"const SCENE_VIDS = new Set\(\[[^\]]*\]\);",
                 "const SCENE_VIDS = new Set([]);  /* this build ships no clips */")

    # 8. The leaderboard and the cloud saves call axesandaces.com.
    if cfg["online"]:
        # The package is served from the portal's own domain, so a relative
        # path would look for the leaderboard there and never find it. The
        # game's functions already answer any origin, so name the site. If the
        # call fails the panels say so and the game plays on regardless.
        p.sub("reach the real leaderboard from the portal's domain",
              "const API=REMOTE+'.netlify/functions/';",
              "const API='https://axesandaces.com/.netlify/functions/';")
    else:
        p.sub("stop every call off the page",
              "async function api(path, body){",
              "async function api(path, body){\n"
              "  /* This build is not allowed to call anything outside itself. */\n"
              "  throw new Error('Online play is off in this build');\n"
              "  // eslint-disable-next-line no-unreachable")
        p.sub("take the online buttons out of the menu",
              '      <button class="btn big ghost" data-act="lb">Leaderboard</button>\n'
              '      <button class="btn big ghost" data-act="cloud">Cloud save</button>\n', "")
        p.sub("take the cloud button off the hero screen",
              """<div class="row"><button class="btn big ghost" data-act="cloud">"""
              """${anySlots()?'Cloud save':'I have a cloud code'}</button>\n"""
              """    <button class="btn big ghost daily" data-act="daily">Daily Challenge</button></div>""",
              """<div class="row"><button class="btn big ghost daily" data-act="daily">"""
              """Daily Challenge</button></div>""")
        p.sub("take posting a level off the death screen",
              """${nameRow()}<div class="row" style="width:100%"><button class="btn big" data-act="postScore" """
              """data-board="level" data-score="${(S.world||0)*1000+S.level}">Post my level</button>"""
              """<button class="btn big brag-fb" data-act="brag" data-kind="death">Make a poster</button>"""
              """</div><div id="lbList"></div>""",
              """<div class="row" style="width:100%"><button class="btn big brag-fb" data-act="brag" """
              """data-kind="death">Make a poster</button></div>""")
        p.sub("take posting a daily score off the results screen",
              """${nameRow()}<button class="btn big" data-act="postScore" data-board="daily" """
              """data-score="${score}">Post my score</button>""", "")
        p.sub("skip the cloud-code screen for a new hero",
              "if(store.get('aa_secured',false)) storyPanel(); else safetyPanel();",
              "storyPanel();")

    return p


def copy_assets(out, cfg, vid_dir):
    for name, src in [("art", ROOT / "art"), ("img", ROOT / "img"),
                      ("icons", ROOT / "icons"), ("music", ROOT / "music"),
                      ("fonts", HERE / "fonts")]:
        shutil.copytree(src, out / name, dirs_exist_ok=True)
    if cfg["video"]:
        if not vid_dir:
            raise SystemExit("This portal carries the monster clips: pass --vid <folder>.")
        src = pathlib.Path(vid_dir)
        if not src.is_dir():
            raise SystemExit("--vid folder not found: %s" % src)
        shutil.copytree(src, out / "vid", dirs_exist_ok=True)


# dev/portal/harness.py drops a copy of the page with an eval hook in it next to
# the real one, so the screen sweep can drive the game. It must never reach a
# portal, so it is left out of both the measurements and the zip.
NOT_SHIPPED = {"audittest.html"}


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
    ap.add_argument("--vid", help="folder of re-encoded clips (dev/portal/encvid.py)")
    ap.add_argument("--out")
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()

    cfg = PORTALS[a.portal]
    out = pathlib.Path(a.out) if a.out else ROOT / "dist" / a.portal
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    src = (ROOT / "dev" / "game.html").read_text(encoding="utf-8")
    p = patch(src, a.portal, cfg)
    (out / "index.html").write_text(HEAD.format(sdk=cfg["sdk"]) + p.text + TAIL,
                                    encoding="utf-8")
    copy_assets(out, cfg, a.vid)

    files, by, total = measure(out)
    print("\n%s  ->  %s" % (a.portal, out))
    for k in sorted(by):
        n, b = by[k]
        print("  %-10s %5d files %8.1f MB" % (k, n, b / 2 ** 20))
    print("  %-10s %5d files %8.1f MB" % ("TOTAL", len(files), total / 2 ** 20))
    print("  patches applied: %d" % len(p.log))

    if a.zip:
        z = out.parent / ("axes-and-aces-%s.zip" % a.portal)
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for f in sorted(files):
                zf.write(f, f.relative_to(out).as_posix())
        print("  zip        %s  %.1f MB" % (z.name, z.stat().st_size / 2 ** 20))


main()
