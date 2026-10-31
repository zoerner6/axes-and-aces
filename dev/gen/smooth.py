"""Rebuild attack clips: play up to the hit, then retreat by reversing the approach (no snap back)."""
import sys, json, subprocess, numpy as np
HIT = json.load(open('gen/hit.json'))
W, H = 1280, 720
SRC = __import__('os').environ.get('SRC', 'vids'); OUT = __import__('os').environ.get('OUT', 'vid_out')
FWD = set(json.load(open('gen/fwd.json'))) if __import__('os').path.exists('gen/fwd.json') else set()
def frames(f, w=W, h=H, gray=False):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale={w}:{h}' + (',format=gray' if gray else ''), '-f', 'rawvideo', '-pix_fmt', 'gray' if gray else 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, h, w) if gray else np.frombuffer(r, np.uint8).reshape(-1, h, w, 3)
def write(fr, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-', '-vf', 'unsharp=5:5:0.8', '-c:v', 'libx264', '-crf', '26', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    p.stdin.write(np.ascontiguousarray(fr).tobytes()); p.stdin.close(); p.wait()
def run(m, hit):
    src = f'{SRC}/{m}_attack.mp4'
    A = frames(src); G = frames(src, 160, 90, True).astype(float)
    drop = {'babydragon': range(17, 21), 'troll': range(51, 54)}.get(m)
    if drop: keep = [i for i in range(len(A)) if i not in drop]; A = A[keep]; G = G[keep]
    I0 = frames(f'{OUT}/{m}_idle.mp4', 160, 90, True)[0].astype(float)
    n = len(A); h = min(n - 2, int(hit * 24))
    if m in ('dragon', 'babydragon', 'witch') or m in FWD:  # breath and spell clips: play forward, then melt into the standing pose
        I0c = frames(f'{OUT}/{m}_idle.mp4')[0]; k = 14
        out = list(A[:n - k]) + [(A[n - k + t] * (1 - (t + 1) / k) + I0c * ((t + 1) / k)).astype(np.uint8) for t in range(k)]
        write(np.stack(out), f'{OUT}/{m}_attack.mp4'); print(m, 'forward only', len(out)); return
    to0 = np.array([abs(g - I0).mean() for g in G])
    step = np.array([abs(G[i + 1] - G[i]).mean() for i in range(n - 1)])
    # the snap back: the frame after the hit where it lands closest to its start pose soonest
    peak = h + int(np.argmax(to0[h:h + 12]))
    hold = peak + 6
    for i in range(peak, n - 1):
        if to0[i + 1] < to0[i] * 0.6 and step[i] > 10: hold = i; break
    else:
        hold = min(n - 1, peak + 8)
    hold = max(h + 3, min(hold, n - 1))
    # retreat: find the approach frame most like the last kept frame, then play the approach backward
    j = hold if len(sys.argv) < 2 or True else 0
    back = [A[int(round(k))] for k in np.arange(j - 1, -0.01, -1.5)]
    fwd = list(A[:hold + 1])
    for t in range(1, 5):  # blend the join
        a = t / 5; fwd.append((A[hold] * (1 - a) + back[0] * a).astype(np.uint8))
    I0c = frames(f'{OUT}/{m}_idle.mp4')[0]
    tail = [(back[-1] * (1 - t / 6) + I0c * (t / 6)).astype(np.uint8) for t in range(1, 7)]
    out = fwd + back + tail
    write(np.stack(out), f'{OUT}/{m}_attack.mp4')
    print(m, 'hit', h, 'peak', peak, 'cut', hold, 'from', j, 'frames', n, '->', len(out))
if __name__ == '__main__':
    for m in sys.argv[1:]: run(m, HIT.get(m, 1.8))
