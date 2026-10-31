import json,os,time,urllib.request
KEY=os.environ["KIE_API_KEY"]; API="https://api.kie.ai/api/v1/jobs"
def call(url, body=None):
    req=urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
for model,inp in [("elevenlabs/text-to-speech-multilingual-v2",{"text":"Rain hammers the windows.","voice":"AeRdCCKzvd23BpJoofzx"}),("elevenlabs/text-to-dialogue-v3",{"dialogue":[{"text":"Rain hammers the windows.","voice":"AeRdCCKzvd23BpJoofzx"}]})]:
    r=call(f"{API}/createTask",{"model":model,"input":inp}); print(model, inp.get("voice"), r.get("msg"), flush=True)
    if not r.get("data"): time.sleep(10); continue
    t=r["data"]["taskId"]
    for i in range(40):
        time.sleep(4); d=call(f"{API}/recordInfo?taskId={t}")["data"]
        if d["state"] in("success","fail"): print("  ->",d["state"],d.get("failMsg"),(d.get("resultJson") or "")[:100], flush=True); break
