"""Find frames where the picture blanks to white/paper or black for a moment, and replace them with the nearest good frame."""
import subprocess, numpy as np, glob, os, sys
W, H = 1280, 720
def read(f):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, H, W, 3)
def write(fr, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-', '-c:v', 'libx264', '-crf', '26', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(fr).tobytes()); p.stdin.close(); p.wait()
fixed = []
for f in sorted(glob.glob('vid_hd/*.mp4')):
    A = read(f); g = A[:, ::8, ::8].mean(axis=(1, 2, 3)); sat = A[:, ::8, ::8].astype(float).std(axis=3).mean(axis=(1, 2))
    base = np.median(g); sm = A[:, ::8, ::8]; white = (sm.min(axis=3) > 190).mean(axis=(1, 2)); wbase = np.median(white)
    bad = [i for i in range(len(A)) if (g[i] > base + 70 and g[i] > 150 and sat[i] < np.median(sat) * .8) or g[i] < base * .35 or (white[i] > .22 and white[i] > wbase + .18)]
    if not bad: continue
    good = [i for i in range(len(A)) if i not in bad]
    B = A.copy()
    for i in bad: B[i] = A[min(good, key=lambda k: abs(k - i))]
    write(B, f); m = os.path.basename(f)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', 'scale=854:-2', '-c:v', 'libx264', '-crf', '28', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', f'vid_out/{m}'] if not os.path.exists(f'vids/{m}') else ['cp', f, f'vid_out/{m}'])
    fixed.append((m, len(bad))); print('fixed', m, len(bad), flush=True)
print('done', len(fixed))
