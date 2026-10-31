"""Build the stand-alone website / installable app version of the game into site/."""
import os, shutil, re, json
from PIL import Image
S = "site"; os.makedirs(f"{S}/icons", exist_ok=True)
g = open("game.html").read()
used = set(re.findall(r"art/[A-Za-z0-9_\-]+\.webp", g))
head = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#14100d"><meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="Axes & Aces">
<meta name="description" content="Axes & Aces: a free dark comic card adventure. Fight monsters with poker hands.">
<meta property="og:type" content="website"><meta property="og:site_name" content="Axes &amp; Aces"><meta property="og:title" content="Axes &amp; Aces: fight monsters with poker hands">
<meta property="og:description" content="Save Anna, become Sir Edward, conquer 10 quests and the Endless Abyss. Free in your browser.">
<meta property="og:image" content="https://axesandaces.com/b/game.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="https://axesandaces.com/"><meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.json"><link rel="icon" href="icons/icon-192.png"><link rel="apple-touch-icon" href="icons/icon-180.png">
<style>html,body{height:100%}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:dark}body{margin:0;font:14px system-ui,sans-serif;background:#14100d}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
tail = """<script>if('serviceWorker' in navigator) addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));</script></body></html>"""
open(f"{S}/play.html", "w").write(head + g + tail)
open(f"{S}/index.html", "w").write(open("landing.html").read())
os.makedirs(f"{S}/img", exist_ok=True)
Image.open("/home/user/axes-and-aces/store/google-play/phone-2-fight.png").convert("RGB").resize((540, 960), Image.LANCZOS).save(f"{S}/img/phone-fight.jpg", quality=86)
for d in ("art", "vid", "music"): os.makedirs(f"{S}/{d}", exist_ok=True)
for f in os.listdir("music"):
    if f.endswith(".mp3"): shutil.copy2(f"music/{f}", f"{S}/music/{f}")
for f in os.listdir("art"):
    if f.endswith(".webp") and not f.endswith("_old.webp"): shutil.copy2(f"art/{f}", f"{S}/art/{f}")
for f in os.listdir("vid_hd"):
    if f.endswith(".mp4"): shutil.copy2(f"vid_hd/{f}", f"{S}/vid/{f}")
ic = Image.open("raw32/appicon_a.jpg").convert("RGB")
for n in (180, 192, 512): ic.resize((n, n), Image.LANCZOS).save(f"{S}/icons/icon-{n}.png")
m = Image.new("RGB", (512, 512), (90, 10, 14)); m.paste(ic.resize((410, 410), Image.LANCZOS), (51, 51)); m.save(f"{S}/icons/maskable-512.png")
json.dump({"name": "Axes & Aces", "short_name": "Axes & Aces", "description": "Fight monsters with poker hands.", "start_url": "./play.html", "scope": "./", "display": "fullscreen",
           "orientation": "any", "background_color": "#14100d", "theme_color": "#14100d",
           "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                     {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, open(f"{S}/manifest.json", "w"), indent=1)
open(f"{S}/sw.js", "w").write("""const C='aa-v4';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','play.html','manifest.json'])));});
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin||/\\/vid\\//.test(u.pathname)) return;
  if(/\\/(art|icons)\\//.test(u.pathname)){ e.respondWith(caches.open(C).then(async c=>{const r=await c.match(e.request); if(r) return r; const n=await fetch(e.request); if(n.ok&&n.status===200) c.put(e.request,n.clone()); return n;})); return; }
  e.respondWith(fetch(e.request,{cache:'no-cache'}).then(n=>{caches.open(C).then(c=>c.put(e.request,n.clone()));return n;}).catch(()=>caches.match(e.request)));});
""")
print("site built", sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(S) for f in fs) // 1e6, "MB")
