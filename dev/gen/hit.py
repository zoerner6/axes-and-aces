import subprocess, glob, os, json, numpy as np
out={}
for f in sorted(glob.glob('vids/*_attack.mp4')):
    k=os.path.basename(f)[:-11]
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-t','3','-vf','fps=10,scale=64:36,format=gray','-f','rawvideo','-'],capture_output=True).stdout
    a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,36,64).astype(float)
    d=[np.abs(x-a[0]).mean() for x in a]
    i=int(np.argmax(d[3:]))+3   # ignore the first 0.3s
    out[k]=round(i/10,1)
print(json.dumps(out))
json.dump(out,open('gen/hit.json','w'))
