"""Generate Axes & Aces art with Kie nano-banana-2. Usage: python3 kie.py jobs.json outdir"""
import json, os, sys, time, urllib.request

KEY = os.environ["KIE_API_KEY"]
API = "https://api.kie.ai/api/v1/jobs"
REF = "https://tempfile.aiquickdraw.com/as/11797cfd72382065b6e01bd54dcfaa60_1793276381246.jpeg"
STYLE = ("Dark comic book art style exactly matching the reference image: thick bold black ink outlines, hard-edged cel shading, "
         "halftone dot texture, rich saturated colors with deep crimson, gold and teal accents, modern dark comic cover look. ")


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for k in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if k == 5: raise
            time.sleep(5 * (k + 1))


def main(jobs_file, out):
    jobs = json.load(open(jobs_file))
    os.makedirs(out, exist_ok=True)
    tasks = json.load(open(f"{out}/tasks.json")) if os.path.exists(f"{out}/tasks.json") else {}
    for j in jobs:
        if os.path.exists(f"{out}/{j['id']}.jpg") or j["id"] in tasks:
            continue
        refs = ([] if j.get("noref") else [REF]) + j.get("refs", [])
        body = {"model": "nano-banana-2", "input": {"prompt": STYLE + j["prompt"], "image_input": refs,
                                                   "aspect_ratio": j.get("ar", "1:1"), "resolution": "1K"}}
        for attempt in range(20):
            r = call(f"{API}/createTask", body)
            if r.get("data"): break
            print("retry", j["id"], r.get("msg"), flush=True); time.sleep(10)
        tasks[j["id"]] = r["data"]["taskId"]
        json.dump(tasks, open(f"{out}/tasks.json", "w"))
        print("queued", j["id"], flush=True)
    while tasks:
        time.sleep(6)
        for jid, tid in list(tasks.items()):
            d = call(f"{API}/recordInfo?taskId={tid}")["data"]
            if d["state"] == "success":
                u = json.loads(d["resultJson"])["resultUrls"][0]
                urllib.request.urlretrieve(u, f"{out}/{jid}.jpg")
                open(f"{out}/{jid}.url", "w").write(u)
                print("done", jid, flush=True); del tasks[jid]
            elif d["state"] == "fail":
                print("FAIL", jid, d.get("failMsg"), flush=True); del tasks[jid]


main(sys.argv[1], sys.argv[2])
