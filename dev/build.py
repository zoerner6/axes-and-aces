"""Build the website from the source files in dev/.
Run from the repo root:  python dev/build.py
Writes play.html (the game, from dev/game.html) and index.html (the front page, from dev/landing.html),
plus sw.js. Art, videos and music already live in art/, vid/ and music/ at the repo root."""
import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
S = "."
g = open("dev/game.html", encoding="utf-8").read()
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
open("play.html", "w", encoding="utf-8").write(head + g + tail)
open("index.html", "w", encoding="utf-8").write(open("dev/landing.html", encoding="utf-8").read())
open("sw.js", "w", encoding="utf-8").write("""const C='aa-v4';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','play.html','manifest.json'])));});
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin||/\\/vid\\//.test(u.pathname)) return;
  if(/\\/(art|icons)\\//.test(u.pathname)){ e.respondWith(caches.open(C).then(async c=>{const r=await c.match(e.request); if(r) return r; const n=await fetch(e.request); if(n.ok&&n.status===200) c.put(e.request,n.clone()); return n;})); return; }
  e.respondWith(fetch(e.request,{cache:'no-cache'}).then(n=>{caches.open(C).then(c=>c.put(e.request,n.clone()));return n;}).catch(()=>caches.match(e.request)));});
""")
print("built index.html, play.html and sw.js")
