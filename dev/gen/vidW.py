"""Idle + attack clips (Seedance 2 Mini, 720p) for the new worlds' monsters, world by world, as starting frames appear."""
import json, os, time, urllib.request
KEY = os.environ["KIE_API_KEY"]; API = "https://api.kie.ai/api/v1/jobs"; OUT = "vidsW"; os.makedirs(OUT, exist_ok=True)
STYLE = "Keep the exact drawing style, colors and ink outlines of the image. Static camera, the background stays completely still. "
W = json.load(open("worlds/worlds.json"))
def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
state = json.load(open(f"{OUT}/tasks.json")) if os.path.exists(f"{OUT}/tasks.json") else {}
def save(): json.dump(state, open(f"{OUT}/tasks.json", "w"))
todo = []
for w in W:
    for a in w["areas"]:
        for m in a["pool"] + [a["boss"]]:
            todo.append((f"{m['slug']}_idle", m["slug"], STYLE + f"The creature ({m['desc']}) stays in place in its fighting stance, breathing heavily, shifting its weight slightly, glaring and snarling at the viewer. Small natural movements only. It ends in exactly the same pose as it starts.", 5))
            todo.append((f"{m['slug']}_attack", m["slug"], STYLE + f"The creature ({m['desc']}) suddenly lunges forward toward the camera and {m['atk']} at the viewer, then slowly backs away to exactly the same starting pose and spot. No cuts, one continuous shot.", 4))
def credits():
    try: return call("https://api.kie.ai/api/v1/chat/credit")["data"]
    except Exception: return 9999
def poll():
    for jid, v in state.items():
        if v["done"]: continue
        try: d = call(f"{API}/recordInfo?taskId={v['task']}")["data"]
        except Exception: continue
        if d["state"] == "success":
            u = json.loads(d["resultJson"])["resultUrls"][0]
            try: urllib.request.urlretrieve(u, f"{OUT}/{jid}.mp4"); v["done"] = True; save(); print("done", jid, flush=True)
            except Exception as e: print("dl err", jid, e, flush=True)
        elif d["state"] == "fail": v["done"] = True; v["fail"] = d.get("failMsg"); save(); print("FAIL", jid, d.get("failMsg"), flush=True)
t0 = time.time()
while time.time() - t0 < 2 * 3600:
    pending = [t for t in todo if t[0] not in state]
    for jid, slug, prompt, dur in pending:
        fu = f"wraw2/frame_{slug}.url"
        if not os.path.exists(fu): continue
        if sum(1 for v in state.values() if not v["done"]) >= 12: break
        if credits() < 60: print("LOW CREDITS", flush=True); break
        fr = open(fu).read().strip()
        body = {"model": "bytedance/seedance-2-mini", "input": {"prompt": prompt, "first_frame_url": fr, "last_frame_url": fr, "resolution": "720p", "aspect_ratio": "16:9", "duration": dur, "generate_audio": False}}
        try: r = call(f"{API}/createTask", body)
        except Exception as e: r = {"msg": str(e)}
        if not r.get("data"): print("retry later", jid, r.get("msg"), flush=True); time.sleep(10); break
        state[jid] = {"task": r["data"]["taskId"], "done": False}; save(); print("queued", jid, flush=True); time.sleep(2)
    poll()
    if all(t[0] in state for t in todo) and all(v["done"] for v in state.values()): break
    time.sleep(15)
print("finished", sum(1 for v in state.values() if v.get("done") and not v.get("fail")), "ok", flush=True)
