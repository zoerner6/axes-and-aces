"""Background music per world plus a boss theme (Suno via Kie). Output music/<id>.mp3"""
import json,os,urllib.request,time
KEY=os.environ["KIE_API_KEY"]
def call(url, body=None):
    req=urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
T={"w1":"medieval tavern adventure, lute, fiddle, bodhran, warm and brave, dark fantasy folk",
"w2":"frozen mountains, icy bells, low strings, wind, cold and mysterious fantasy",
"w3":"desert sands, oud, darbuka, hot and tense, ancient tombs fantasy",
"w4":"sunken coast, sea shanty strings, accordion, waves, ghostly sailors",
"w5":"plague marsh, eerie swamp, low clarinet, croaking percussion, creepy fantasy",
"w6":"iron mines, anvil hits, deep brass, dwarven forge rhythm, heavy",
"w7":"haunted abbey, pipe organ, choir pads, gothic, spooky",
"w8":"enchanted elven forest, harp, flute, dark magical woods",
"w9":"sky fortress, thunder, soaring strings, heroic storm battle",
"w10":"demon abyss, hellish drums, distorted choir, epic dark final battle",
"boss":"intense boss battle, war drums, brass, choir, epic dark fantasy combat"}
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
