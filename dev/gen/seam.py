"""How visible is each standing loop's restart? ratio = jump at the seam / normal frame-to-frame motion."""
import subprocess, glob, os, json, numpy as np
out = {}
for f in sorted(glob.glob('vid_hd/*_idle.mp4')):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', 'scale=160:90,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    A = np.frombuffer(r, np.uint8).reshape(-1, 90, 160).astype(float)
    step = np.median([abs(A[i + 1] - A[i]).mean() for i in range(len(A) - 1)])
    seam = abs(A[0] - A[-1]).mean()
    out[os.path.basename(f)[:-9]] = round(seam / max(step, .3), 1)
json.dump(out, open('gen/seam.json', 'w'))
bad = {k: v for k, v in sorted(out.items(), key=lambda x: -x[1]) if v > 2.5}
print(len(out), 'loops,', len(bad), 'jumpy:', bad)
