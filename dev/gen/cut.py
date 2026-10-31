import sys, glob, os
from rembg import remove, new_session
from PIL import Image
sess = new_session("isnet-general-use")
def cut(src, dst, h):
    im = Image.open(src).convert("RGB")
    out = remove(im, session=sess)
    bb = out.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()
    out = out.crop(bb)
    out.thumbnail((h * 2, h))
    out.save(dst, "WEBP", quality=82, method=6)
for f in sys.argv[2:]:
    name = os.path.basename(f)[:-4]
    cut(f, f"art/{name.split('_',1)[1] if name.startswith('m_') else name}.webp", int(sys.argv[1]))
    print("cut", name, flush=True)
