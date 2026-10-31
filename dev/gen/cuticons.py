import glob, os
from rembg import remove, new_session
from PIL import Image
sess=new_session("isnet-general-use")
for f in sorted(glob.glob("raw14/i_*.jpg")):
    out=remove(Image.open(f).convert("RGB"), session=sess)
    out=out.crop(out.getchannel("A").point(lambda a:255 if a>20 else 0).getbbox())
    w,h=out.size; m=max(w,h); sq=Image.new("RGBA",(m,m),(0,0,0,0)); sq.paste(out,((m-w)//2,(m-h)//2)); sq=sq.resize((128,128),Image.LANCZOS)
    sq.save("art/"+os.path.basename(f)[:-4]+".webp","WEBP",quality=85,method=6)
for src,dst in []:
    dst=dst.replace("start_1b","start_1")
    im=Image.open(src).convert("RGB"); im.thumbnail((1100,620)); im.save(f"art/{dst}.webp","WEBP",quality=74,method=6)
print("ok")
