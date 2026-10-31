"""Turn the new-world raw pictures (wraw/) into game art (art/)."""
import glob, os, sys
from rembg import remove, new_session
from PIL import Image
sess = new_session("isnet-general-use")
src = sys.argv[1] if len(sys.argv) > 1 else "wraw"
def cutout(f):
    out = remove(Image.open(f).convert("RGB"), session=sess)
    return out.crop(out.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox())
for f in sorted(glob.glob(f"{src}/*.jpg")):
    n = os.path.basename(f)[:-4]
    if n.startswith("m_"):
        dst = f"art/{n[2:]}.webp"
        if os.path.exists(dst): continue
        o = cutout(f); o.thumbnail((840, 420)); o.save(dst, "WEBP", quality=82, method=6)
    elif n.startswith("ko_"):
        dst = f"art/dead_{n[3:]}.webp"
        if os.path.exists(dst): continue
        o = cutout(f); o.thumbnail((520, 420)); o.save(dst, "WEBP", quality=82, method=6)
    elif n.startswith("i_"):
        dst = f"art/{n}.webp"
        if os.path.exists(dst): continue
        o = cutout(f); w, h = o.size; m = max(w, h); sq = Image.new("RGBA", (m, m), (0, 0, 0, 0)); sq.paste(o, ((m - w) // 2, (m - h) // 2))
        sq.resize((128, 128), Image.LANCZOS).save(dst, "WEBP", quality=85, method=6)
    elif n.startswith("bg_") or n.startswith("sc_"):
        dst = f"art/{n}.webp"
        if os.path.exists(dst): continue
        im = Image.open(f).convert("RGB"); im.thumbnail((1280, 720) if n.startswith("bg_") else (1100, 620)); im.save(dst, "WEBP", quality=74, method=6)
    else: continue
    print("ok", n, flush=True)
print("all done")
