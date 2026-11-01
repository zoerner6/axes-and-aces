"""Build audittest.html the way build.py builds play.html, plus the eval hook.
  python dev/gen/harness.py [source.html] [out.html]
The viewport meta matters: without it a mobile-emulated Chrome lays the page
out at 980px and every max-width media query in the game reads false.
"""
import re, sys, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
src = sys.argv[1] if len(sys.argv) > 1 else "dev/game.html"
out = sys.argv[2] if len(sys.argv) > 2 else "audittest.html"
build = open("dev/build.py", encoding="utf-8").read()
# Each game on the site keeps its head in its own variable in dev/build.py, so a
# test page can never drift from the real page. Match the assignment at the
# start of a line, or `head` would also be found inside `fhead`.
HEADVAR = {"farkle": "fhead"}
var = HEADVAR.get(os.path.splitext(os.path.basename(src))[0], "head")
m = re.search('^' + var + ' = """(.*?)"""', build, re.S | re.M)
assert m, "could not find " + var + ' = """..."""' + " in dev/build.py"
head = m.group(1)
g = open(src, encoding="utf-8").read()
h = g.rfind("})();")
assert h > 0, "could not find the end of the game IIFE"
g = g[:h] + "window.__A={ev:x=>eval(x)};\n" + g[h:]
open(out, "w", encoding="utf-8").write(head + g + "</body></html>")
print("wrote", out, len(head + g))
