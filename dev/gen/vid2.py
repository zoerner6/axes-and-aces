import json, os, sys, time, urllib.request
KEY=os.environ["KIE_API_KEY"]; API="https://api.kie.ai/api/v1/jobs"; FR=sys.argv[1]; OUT="vid"
P2=("Animate this illustration, keeping its exact drawing style, colors and outlines. Static camera. The green creature with pointed ears stands in a fighting stance, breathing heavily, shoulders rising and falling, shifting its weight and snarling at the viewer while the fire flickers behind it. Then it suddenly lunges toward the camera, swings its knife across the screen, and hops back into its stance. The room stays still.")
P=("Dark comic book animation, keep the exact art style, colors and ink outlines of the image. Static camera. The green goblin stands in his fighting stance, "
   "breathing heavily, shoulders rising and falling, shifting his weight, glaring and snarling at the viewer, the fire flickering behind him. "
   "Then he suddenly lunges forward toward the camera and slashes his dagger across the screen, then hops back into his stance. Background stays still.")
JOBS0={
 'budget':{"model":"bytedance/seedance-2-mini","input":{"prompt":P,"first_frame_url":FR,"resolution":"720p","aspect_ratio":"16:9","duration":6,"generate_audio":False}},
 'good':  {"model":"wan/3-0-video","input":{"prompt":P,"first_frame_url":FR,"resolution":"720P","aspect_ratio":"16:9","duration":6,"audio":False}},
 'best':  {"model":"kling-3.0/video","input":{"prompt":P,"image_urls":[FR],"duration":"6","mode":"std","sound":False,"multi_shots":False}},
}
JOBS={'best':{"model":"kling-3.0/video","input":{"prompt":P2,"image_urls":[FR],"duration":"6","mode":"std","sound":False,"multi_shots":False}}}
def call(url, body=None):
    req=urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
tasks={}
for k,b in JOBS.items():
    r=call(f"{API}/createTask", b); print(k, r.get("code"), r.get("msg"), flush=True)
    if r.get("data"): tasks[k]=r["data"]["taskId"]
    time.sleep(3)
t0=time.time()
while tasks and time.time()-t0<1500:
    time.sleep(10)
    for k,t in list(tasks.items()):
        try: d=call(f"{API}/recordInfo?taskId={t}")["data"]
        except Exception as e: print("poll err",e,flush=True); continue
        if d["state"]=="success":
            u=json.loads(d["resultJson"])["resultUrls"][0]; urllib.request.urlretrieve(u, f"{OUT}/goblin_{k}.mp4"); print("done",k,int(time.time()-t0),"s",flush=True); del tasks[k]
        elif d["state"]=="fail": print("FAIL",k,d.get("failMsg"),flush=True); del tasks[k]
print("left",list(tasks))
