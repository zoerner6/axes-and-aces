import glob, os
from rembg import remove, new_session
from PIL import Image
sess=new_session("isnet-general-use")
for f in sorted(glob.glob("raw20/ko_*.jpg")):
    out=remove(Image.open(f).convert("RGB"), session=sess)
    out=out.crop(out.getchannel("A").point(lambda a:255 if a>20 else 0).getbbox()); out.thumbnail((520,420))
    out.save("art/"+os.path.basename(f)[:-4].replace("ko_","dead_")+".webp","WEBP",quality=82,method=6)
print("ok")
