"""Zip a package that is already built, without rebuilding it.

`build_portal.py --zip` does this at the end of a build. This is for when the
folder is already there and something else is reading it, which on Windows means
a rebuild would fail anyway.

  python dev/portal/zip_portal.py crazygames poki
"""
import pathlib, sys, zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
# The audit page carries an eval hook for the screen sweep. It never ships.
NOT_SHIPPED = {"audittest.html"}


def zip_one(name):
    src = ROOT / "dist" / name
    if not src.is_dir():
        raise SystemExit(f"not built yet: {src}")
    files = sorted(p for p in src.rglob("*")
                   if p.is_file() and p.name not in NOT_SHIPPED)
    dst = src.parent / f"axes-and-aces-{name}.zip"
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            z.write(f, f.relative_to(src).as_posix())
    total = sum(f.stat().st_size for f in files)
    print(f"  {dst.name:<34} {len(files):>5} files"
          f"  {total/2**20:>7.1f} MB unpacked"
          f"  {dst.stat().st_size/2**20:>7.1f} MB zipped")


for n in (sys.argv[1:] or ["crazygames", "poki"]):
    zip_one(n)
