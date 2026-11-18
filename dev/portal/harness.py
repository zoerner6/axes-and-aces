"""Make a portal package auditable: take its index.html and add the eval hook
dev/gen/mobscan.cjs drives the screens through.

  python dev/portal/harness.py dist/crazygames
"""
import pathlib, sys

d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist/crazygames")
g = (d / "index.html").read_text(encoding="utf-8")
# The game's body is handed to AABOOT, so the package ends "});" rather than
# the "})();" dev/game.html closes with.
h = g.rfind("\n});\n</script>") + 1
assert h > 0, "could not find the end of the game body"
out = d / "audittest.html"
out.write_text(g[:h] + "window.__A={ev:x=>eval(x)};\n" + g[h:], encoding="utf-8")
print("wrote", out)
