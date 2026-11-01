/* Does a whole world finish and hand over to the next one?
   Walks the arc by winning fights outright rather than playing them, so the
   twelve-fight shape and the world handover get checked without a long game.
     node dev/gen/fkarc.cjs */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
execFileSync('python', ['dev/gen/harness.py','dev/farkle.html','farkletest.html'], {stdio:'inherit'});
const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
const srv = http.createServer((q,r)=>{
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'') || 'farkletest.html';
  const f = path.join(ROOT, rel);
  if(!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ r.writeHead(404); return r.end('no'); }
  r.writeHead(200,{'content-type':MIME[path.extname(f).toLowerCase()]||'application/octet-stream'});
  fs.createReadStream(f).pipe(r);
});
(async()=>{
  await new Promise(z=>srv.listen(0,'127.0.0.1',z));
  const base=`http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const p=await ctx.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  p.on('console',m=>{ if(m.type()==='error'&&!/404/.test(m.text())) errs.push(m.text().slice(0,140)); });
  await p.goto(base,{waitUntil:'load'}); await p.waitForTimeout(700);
  const q = js => p.evaluate(x=>window.__A.ev(x), js);
  const seen = [];
  /* clear the opening story */
  for(let i=0;i<6;i++){
    const btn = await p.$('#overlay:not([hidden]) [data-act="storyNext"]');
    if(!btn) break;
    await btn.click(); await p.waitForTimeout(500);
  }
  for(let fight=0; fight<26; fight++){
    const st = await p.evaluate(()=>({
      w: window.__FK.S.world, idx: window.__FK.S.idx,
      foe: window.__FK.S.fight && window.__FK.S.fight.d.name,
      boss: !!(window.__FK.S.fight && window.__FK.S.fight.d.boss),
      overlay: !document.getElementById('overlay').hidden,
      acts: [...document.querySelectorAll('#overlay [data-act]')].map(x=>x.dataset.act),
    }));
    if(st.foe) seen.push(`w${st.w}.${st.idx}${st.boss?'B':''} ${st.foe}`);
    /* clear whatever popup is up, then win the fight outright */
    if(st.overlay){
      for(const a of ['storyNext','fight','onward','perk','leaveShop','again']){
        const btn = await p.$(`#overlay:not([hidden]) [data-act="${a}"]`);
        if(btn){ await btn.click(); await p.waitForTimeout(450); break; }
      }
      fight--; continue;
    }
    await q('busy=false; S.hp=S.maxHp; S.tookHit=false; S.fight.hp=0; won();');
    await p.waitForTimeout(1900);
  }
  const end = await p.evaluate(()=>({ w: window.__FK.S.world, lv: window.__FK.S.level }));
  await b.close(); srv.close();
  console.log(seen.join('\n'));
  console.log(`\nreached world ${end.w} ("${['Anna','Frozen Peaks','Burning Sands'][end.w]||'?'}"), level ${end.lv}`);
  console.log('js errors:', errs.length ? errs.slice(0,4) : 'none');
  const ok = end.w >= 1 && !errs.length;
  console.log(ok ? '\nA whole world finishes and hands over to the next.' : '\nTHE ARC DOES NOT COMPLETE.');
  process.exit(ok?0:1);
})();
