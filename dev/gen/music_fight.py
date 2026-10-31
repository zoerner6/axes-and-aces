"""Background music per world plus a boss theme (Suno via Kie). Output music/<id>.mp3"""
import json,os,urllib.request,time
KEY=os.environ["KIE_API_KEY"]
def call(url, body=None):
    req=urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
T={"fight1":"tense suspenseful battle music, low staccato strings, taiko and war drums, dark brass stabs, rising tension, medieval fantasy combat",
"fight2":"suspenseful dark fantasy fight music, driving ostinato cellos, pounding frame drums, ominous low horns, urgent and gritty"}
state=json.load(open('music/tasks.json')) if os.path.exists('music/tasks.json') else {}
for k,style in T.items():
    if k in state or os.path.exists(f'music/{k}.mp3'): continue
    r=call("https://api.kie.ai/api/v1/generate",{"prompt":"","style":"instrumental loopable background game music, no vocals, "+style,"title":k,"customMode":True,"instrumental":True,"model":"V4_5","callBackUrl":"https://example.com/cb"})
    state[k]=r["data"]["taskId"]; json.dump(state,open('music/tasks.json','w')); print("queued",k,flush=True); time.sleep(3)
left=dict(state)
for i in range(120):
    for k,t in list(left.items()):
        if os.path.exists(f'music/{k}.mp3'): left.pop(k); continue
        a=call(f"https://api.kie.ai/api/v1/generate/record-info?taskId={t}")['data']
        if a.get('status')=='SUCCESS':
            u=a['response']['sunoData'][0]['audio_url']; urllib.request.urlretrieve(u,f'music/{k}_raw.mp3')
            os.system(f"ffmpeg -v error -y -i music/{k}_raw.mp3 -ac 1 -b:a 80k music/{k}.mp3"); left.pop(k); print("done",k,flush=True)
        elif 'FAIL' in str(a.get('status')): left.pop(k); print("FAIL",k,a.get('errorMessage'),flush=True)
    if not left: break
    time.sleep(15)
print("all done",flush=True)
