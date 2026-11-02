const C='aa-v4';
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','play.html','farkle.html','manifest.json'])));});
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin||/\/vid\//.test(u.pathname)) return;
  if(/\/(art|icons|img)\//.test(u.pathname)){ e.respondWith(caches.open(C).then(async c=>{const r=await c.match(e.request); if(r) return r; const n=await fetch(e.request); if(n.ok&&n.status===200) c.put(e.request,n.clone()); return n;})); return; }
  e.respondWith(fetch(e.request,{cache:'no-cache'}).then(n=>{caches.open(C).then(c=>c.put(e.request,n.clone()));return n;}).catch(()=>caches.match(e.request)));});
