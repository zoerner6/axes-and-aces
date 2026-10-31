import json, os, time, urllib.request, sys
KEY=os.environ["KIE_API_KEY"]; API="https://api.kie.ai/api/v1/jobs"; OUT="art"
VOICE=sys.argv[1] if len(sys.argv)>1 else "AeRdCCKzvd23BpJoofzx"
def call(url, body=None):
    req=urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
for j in json.load(open("gen/vo.json")):
    if os.path.exists(f"{OUT}/{j['id']}.mp3"): continue
    for attempt in range(4):
        body={"model":"elevenlabs/text-to-speech-multilingual-v2","input":{"text":j["text"],"voice":VOICE,"stability":0.45,"similarity_boost":0.75,"style":0.3,"speed":0.95}}
        r=call(f"{API}/createTask", body)
        if not r.get("data"): print("busy", r.get("msg"), flush=True); time.sleep(15); continue
        t=r["data"]["taskId"]; d={"state":"waiting"}
        for k in range(60):
            time.sleep(4); d=call(f"{API}/recordInfo?taskId={t}")["data"]
            if d["state"] in ("success","fail"): break
        if d["state"]=="success":
            u=json.loads(d["resultJson"])["resultUrls"][0]; urllib.request.urlretrieve(u, f"{OUT}/{j['id']}.mp3"); print("done", j["id"], flush=True); break
        print("fail", j["id"], d.get("failMsg"), flush=True); time.sleep(10)
