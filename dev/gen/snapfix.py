"""Standing clips that snap back near the end: cut before the snap, then rebuild a seamless loop."""
import subprocess, numpy as np, sys, os
FPS = 24
def frames(f):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-vf', 'fps=24,scale=160:90,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, 90, 160).astype(float)
def run(cmd): subprocess.run(cmd, check=True)
for m in sys.argv[1:]:
    src = f'vids/{m}_idle.mp4' if os.path.exists(f'vids/{m}_idle.mp4') else f'vidsW/{m}_idle.mp4'
    A = frames(src); d = np.array([abs(A[i + 1] - A[i]).mean() for i in range(len(A) - 1)]); med = np.median(d)
    jumps = [i for i, x in enumerate(d) if x > 4 and x > 10 * med and i > 30]
    end = (jumps[0] - 1) if jumps else len(A) - 1
    T = round(end / FPS, 3)
    if m in ('rat', 'boar', 'goblin', 'imp'):
        fc = f"[0:v]fps=24,trim=end={T},setpts=PTS-STARTPTS,split[a][b];[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1,unsharp=5:5:0.8[o]"
    else:
        x = min(0.8, T / 4); off = round(T - 2 * x, 3)
        fc = f"[0:v]fps=24,trim=end={T},setpts=PTS-STARTPTS,split[a][b];[a]trim=start={x},setpts=PTS-STARTPTS[A];[b]trim=end={x},setpts=PTS-STARTPTS[B];[A][B]xfade=transition=fade:duration={x}:offset={off},unsharp=5:5:0.8[o]"
    run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[o]', '-c:v', 'libx264', '-crf', '26', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', f'vid_hd/{m}_idle.mp4'])
    w1 = os.path.exists(f'vids/{m}_idle.mp4')
    if w1: run(['cp', f'vid_hd/{m}_idle.mp4', f'vid_out/{m}_idle.mp4'])
    else: run(['ffmpeg', '-v', 'error', '-y', '-i', f'vid_hd/{m}_idle.mp4', '-vf', 'scale=854:-2', '-c:v', 'libx264', '-crf', '28', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-an', '-movflags', '+faststart', f'vid_out/{m}_idle.mp4'])
    print(m, 'cut at', T, 's', flush=True)
