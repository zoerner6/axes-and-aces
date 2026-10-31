"""Make idle + attack clips (Seedance 2 Mini) for every monster that has a starting frame."""
import json, os, time, urllib.request, glob
KEY=os.environ["KIE_API_KEY"]; API="https://api.kie.ai/api/v1/jobs"; OUT="vids"
D=json.load(open("gen/monsters.json"))
STYLE="Keep the exact drawing style, colors and ink outlines of the image. Static camera, the background stays completely still. "
def call(url, body=None):
    req=urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
state=json.load(open(f"{OUT}/tasks.json")) if os.path.exists(f"{OUT}/tasks.json") else {}
def save(): json.dump(state, open(f"{OUT}/tasks.json","w"))
todo=[]
for k,(a,desc,atk) in D.items():
    fu=f"frames/frame_{k}.url"
    if not os.path.exists(fu): continue
    fr=open(fu).read().strip()
    todo.append((f"{k}_idle", fr, STYLE+f"The {desc} stays in place in its fighting stance, breathing heavily, shoulders rising and falling, shifting its weight slightly, glaring and snarling at the viewer. Small natural movements only. It ends in exactly the same pose as it starts.", 5))
    todo.append((f"{k}_attack", fr, STYLE+f"The {desc} suddenly lunges forward toward the camera and {atk} at the viewer, then quickly steps back into exactly the same starting pose.", 4))
for jid,fr,prompt,dur in todo:
    if jid in state or os.path.exists(f"{OUT}/{jid}.mp4"): continue
    body={"model":"bytedance/seedance-2-mini","input":{"prompt":prompt,"first_frame_url":fr,"last_frame_url":fr,"resolution":"720p","aspect_ratio":"16:9","duration":dur,"generate_audio":False}}
    for attempt in range(30):
        try: r=call(f"{API}/createTask", body)
        except Exception as e: r={"msg":str(e)}
        if r.get("data"): break
        print("retry",jid,r.get("msg"),flush=True); time.sleep(12)
    if not r.get("data"): print("GAVE UP",jid,flush=True); continue
    state[jid]={"task":r["data"]["taskId"],"done":False}; save(); print("queued",jid,flush=True); time.sleep(2)
t0=time.time()
while any(not v["done"] for v in state.values()) and time.time()-t0<3000:
    time.sleep(12)
    for jid,v in state.items():
        if v["done"]: continue
        try: d=call(f"{API}/recordInfo?taskId={v['task']}")["data"]
        except Exception as e: continue
        if d["state"]=="success":
            u=json.loads(d["resultJson"])["resultUrls"][0]
            try: urllib.request.urlretrieve(u, f"{OUT}/{jid}.mp4"); v["done"]=True; save(); print("done",jid,flush=True)
            except Exception as e: print("dl err",jid,e,flush=True)
        elif d["state"]=="fail": v["done"]=True; v["fail"]=d.get("failMsg"); save(); print("FAIL",jid,d.get("failMsg"),flush=True)
print("finished", sum(1 for v in state.values() if v.get('done') and not v.get('fail')), "ok")
