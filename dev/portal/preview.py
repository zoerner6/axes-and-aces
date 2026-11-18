"""Cut the recordings from dev/portal/trailer.cjs into the preview videos
CrazyGames accepts: 1080p, 15 to 20 seconds, no sound, no black bars.

The cut starts a couple of seconds before the fight does, so the clip opens on
the boss rather than on a menu, and runs to the end of the recording.

  python dev/portal/preview.py [dev/gen/out/trailer]
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dev/gen/out/trailer")
OUT = ROOT / "store" / "portal"

LEAD = 2.5        # seconds of boss before the fight starts
MAX = 19.5        # their cap is 20; leave a moment's margin
SIZES = {"landscape": (1920, 1080), "portrait": (1080, 1620)}


def cut(name, info):
    w, h = SIZES[name]
    start = max(0.0, info["marks"]["fightStart"] - LEAD)
    dur = min(MAX, info["marks"]["end"] - start)
    dst = OUT / f"preview-{name}-{w}x{h}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", info["src"],
        "-vf", f"scale={w}:{h}:flags=lanczos,format=yuv420p",
        "-c:v", "libx264", "-crf", "20", "-preset", "slow",
        "-profile:v", "high", "-r", "30", "-an", "-movflags", "+faststart",
        str(dst)], check=True)
    size = dst.stat().st_size
    print(f"  {dst.name:<40} {w}x{h}  {dur:>5.1f}s  {size/2**20:>5.1f} MB"
          f"  {'OK' if dur <= 20 and size <= 50*2**20 else 'OVER THE LIMIT'}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    info = json.loads((SRC / "sources.json").read_text(encoding="utf-8"))
    for name in ("landscape", "portrait"):
        cut(name, info[name])


main()
