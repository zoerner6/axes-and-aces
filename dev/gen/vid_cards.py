import json,os,urllib.request,time
KEY=os.environ["KIE_API_KEY"]
def call(url, body=None):
    req=urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
fr=open('raw70/sc_start_2_cards.url').read().strip()
P=("Keep the exact drawing style, colors and ink outlines of the image. Static camera. The old barkeep on the left winds up and flings a fan of glowing playing cards across the tavern; "
   "the cards spin through the air in a fast arc trailing golden sparks and magical energy, like a card-throwing magician. The young hero on the right snaps his hand up and catches the glowing cards, "
   "golden light bursting over his face, then holds the glowing deck up proudly. Fire crackles in the fireplace. One continuous shot, no cuts.")
r=call("https://api.kie.ai/api/v1/jobs/createTask",{"model":"bytedance/seedance-2-mini","input":{"prompt":P,"first_frame_url":fr,"resolution":"720p","aspect_ratio":"16:9","duration":5,"generate_audio":False}})
tid=r["data"]["taskId"]; print("queued",tid,flush=True)
for i in range(120):
    time.sleep(10); d=call(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={tid}")["data"]
    if d["state"]=="success":
        urllib.request.urlretrieve(json.loads(d["resultJson"])["resultUrls"][0],"raw70/cards.mp4"); print("done",flush=True); break
    if d["state"]=="fail": print("FAIL",d.get("failMsg"),flush=True); break
