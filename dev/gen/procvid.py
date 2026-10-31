"""Process new-world clips as they arrive: hit time, sharp HD versions (vid_hd/, website) and lighter ones (vid_out/, artifact)."""
import json, os, subprocess, time, glob, numpy as np
env = dict(os.environ, SRC="vidsW", OUT="vid_hd")
def hit(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-t', '3', '-vf', 'fps=10,scale=64:36,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 36, 64).astype(float)
    d = [np.abs(x - a[0]).mean() for x in a]
    return round((int(np.argmax(d[3:])) + 3) / 10, 1)
def light(m, k):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'vid_hd/{m}_{k}.mp4', '-vf', 'scale=854:-2', '-c:v', 'libx264', '-crf', '28', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', f'vid_out/{m}_{k}.mp4'])
idle_wait = 0
while True:
    H = json.load(open('gen/hit.json'))
    slugs = sorted({os.path.basename(f).rsplit('_', 1)[0] for f in glob.glob('vidsW/*_idle.mp4')})
    todo = [m for m in slugs if os.path.exists(f'vidsW/{m}_attack.mp4') and not os.path.exists(f'vid_out/{m}_attack.mp4')]
    for m in todo:
        try:
            H[m] = hit(f'vidsW/{m}_attack.mp4'); json.dump(H, open('gen/hit.json', 'w'))
            subprocess.run(['bash', 'gen/encidle.sh', 'vidsW', m], env=env)
            subprocess.run(['python3', 'gen/smooth.py', m], env=env)
            light(m, 'idle'); light(m, 'attack'); print('ok', m, H[m], flush=True)
        except Exception as e: print('err', m, e, flush=True)
    running = subprocess.run(['pgrep', '-f', 'gen/vidW.py'], capture_output=True).stdout.strip()
    if not todo and not running:
        idle_wait += 1
        if idle_wait > 3: break
    time.sleep(60)
print('all processed', flush=True)
