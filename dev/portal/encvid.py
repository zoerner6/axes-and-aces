"""Re-encode the monster and scene clips small enough for a games portal.

The clips are 1280x720 at ~1.7Mbps, which is far more than the monster box
ever shows. Scaling down and raising the CRF keeps the monsters moving while
fitting the portal's total-size cap.

  python dev/portal/encvid.py --sample            measure a sample, encode nothing
  python dev/portal/encvid.py --out <dir>         encode every clip into <dir>
"""
import argparse, concurrent.futures as cf, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
VID = ROOT / "vid"
# Idle clips loop for ten seconds and get stared at, so they keep more pixels.
# Attack clips flash past in two to four seconds, and scenes sit behind text.
PROFILE = {"idle": (854, 28), "attack": (768, 30), "scene": (854, 29)}

def kind(p):
    if p.name.startswith("sc_"): return "scene"
    return "attack" if p.stem.endswith("_attack") else "idle"

def encode(src, dst, width, crf):
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                    "-vf", f"scale={width}:-2", "-c:v", "libx264", "-crf", str(crf),
                    "-preset", "medium", "-profile:v", "main", "-pix_fmt", "yuv420p",
                    "-an", "-movflags", "+faststart", str(dst)], check=True)
    return dst.stat().st_size

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out"); ap.add_argument("--sample", action="store_true")
    ap.add_argument("--every", type=int, default=14)
    a = ap.parse_args()
    clips = sorted(VID.glob("*.mp4"))
    total = sum(p.stat().st_size for p in clips)
    if a.sample:
        groups = {}
        for p in clips: groups.setdefault(kind(p), []).append(p)
        picked = [p for g in groups.values() for p in g[::a.every]]
        out = ROOT / ".enc-sample"
        before = sum(p.stat().st_size for p in picked)
        after = 0
        for p in picked:
            w, q = PROFILE[kind(p)]
            after += encode(p, out / p.name, w, q)
        print(f"sample {len(picked)} of {len(clips)} clips")
        print(f"  before {before/2**20:.1f}MB   after {after/2**20:.1f}MB   "
              f"ratio {after/before:.3f}")
        print(f"  all {len(clips)} clips: {total/2**20:.1f}MB -> "
              f"~{total*after/before/2**20:.1f}MB")
        return
    out = pathlib.Path(a.out)
    t0 = time.time()
    jobs = [(p, out / p.name, *PROFILE[kind(p)]) for p in clips]
    done = 0
    with cf.ThreadPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 1)) as ex:
        for _ in ex.map(lambda j: encode(*j), jobs):
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(jobs)}  {time.time()-t0:.0f}s", flush=True)
    after = sum(p.stat().st_size for p in out.glob("*.mp4"))
    print(f"{len(jobs)} clips: {total/2**20:.1f}MB -> {after/2**20:.1f}MB "
          f"in {time.time()-t0:.0f}s")

main()
