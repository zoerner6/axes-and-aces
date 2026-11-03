"""Re-encode the monster clips small enough for a games portal.

The clips in vid/ are 1280x720 at about 1.7Mbps, far more than the monster box
on the stage ever shows. Scaling down and raising the CRF keeps every monster
moving while fitting CrazyGames' total-size cap.

  python dev/portal/farkle/encvid.py --sample          measure a sample, encode nothing
  python dev/portal/farkle/encvid.py --out .vid-small  encode every clip into .vid-small

Needs ffmpeg on the PATH. Takes a while: it is 413 clips.

The card game's dev/portal/encvid.py does the same job with the same profile -
both games show the same clips at the same size, so a folder made by either
one works for either build.
"""
import argparse, concurrent.futures as cf, os, pathlib, subprocess, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
VID = ROOT / "vid"
# Idle clips loop for ten seconds and get stared at, so they keep more pixels.
# Attack clips flash past in two to four seconds, and scenes sit behind text.
PROFILE = {"idle": (854, 28), "attack": (768, 30), "scene": (854, 29)}


def kind(p):
    if p.name.startswith("sc_"):
        return "scene"
    return "attack" if p.stem.endswith("_attack") else "idle"


def encode(src, dst, width, crf):
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                    "-vf", "scale=%d:-2" % width, "-c:v", "libx264", "-crf", str(crf),
                    "-preset", "medium", "-profile:v", "main", "-pix_fmt", "yuv420p",
                    "-an", "-movflags", "+faststart", str(dst)], check=True)
    return dst.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--every", type=int, default=14)
    a = ap.parse_args()
    clips = sorted(VID.glob("*.mp4"))
    if not clips:
        raise SystemExit("No clips in %s" % VID)
    total = sum(p.stat().st_size for p in clips)
    if a.sample:
        groups = {}
        for p in clips:
            groups.setdefault(kind(p), []).append(p)
        picked = [p for g in groups.values() for p in g[::a.every]]
        out = ROOT / ".enc-sample"
        before = sum(p.stat().st_size for p in picked)
        after = 0
        for p in picked:
            w, q = PROFILE[kind(p)]
            after += encode(p, out / p.name, w, q)
        print("sample %d of %d clips" % (len(picked), len(clips)))
        print("  before %.1fMB   after %.1fMB   ratio %.3f"
              % (before / 2 ** 20, after / 2 ** 20, after / before))
        print("  all %d clips: %.1fMB -> ~%.1fMB"
              % (len(clips), total / 2 ** 20, total * after / before / 2 ** 20))
        return
    if not a.out:
        raise SystemExit("Pass --out <dir>, or --sample to measure first.")
    out = pathlib.Path(a.out)
    t0 = time.time()
    jobs = [(p, out / p.name, *PROFILE[kind(p)]) for p in clips]
    done = 0
    with cf.ThreadPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 1)) as ex:
        for _ in ex.map(lambda j: encode(*j), jobs):
            done += 1
            if done % 25 == 0:
                print("  %d/%d  %ds" % (done, len(jobs), time.time() - t0), flush=True)
    after = sum(p.stat().st_size for p in out.glob("*.mp4"))
    print("%d clips: %.1fMB -> %.1fMB in %ds"
          % (len(jobs), total / 2 ** 20, after / 2 ** 20, time.time() - t0))


main()
