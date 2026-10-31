"""Point the game at every monster that has both clips, with its hit timing."""
import json, os, re, glob
g = open('game.html').read()
have = sorted(m for m in {os.path.basename(f)[:-9] for f in glob.glob('vid_out/*_idle.mp4')} if os.path.exists(f'vid_out/{m}_attack.mp4'))
H = json.load(open('gen/hit.json'))
g = re.sub(r"^const VIDS = new Set\(\[.*?\]\);", "const VIDS = new Set(" + json.dumps(have) + ");", g, count=1, flags=re.M)
g = re.sub(r"^const HIT_AT = \{.*?\};", "const HIT_AT = " + json.dumps({k: H[k] for k in have if k in H}) + ";", g, count=1, flags=re.M)
open('game.html', 'w').write(g); print(len(have), 'monsters with video')
