/* Does every encounter say something true about the thing in the picture?
   Runs a lot of real intros and checks the three lines agree with each other
   and with the monster: beasts never speak, the caption names the monster,
   and the bubble matches the kind of meeting it actually is.
     node dev/gen/fkvoice.cjs [rounds] */
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
const N = +(process.argv[2] || 120);
(async()=>{
  await new Promise(z=>srv.listen(0,'127.0.0.1',z));
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const p=await ctx.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto(`http://127.0.0.1:${srv.address().port}/farkletest.html`,{waitUntil:'load'});
  await p.waitForTimeout(700);
  const bad=[]; const seen={beast:0,talker:0,kinds:{}};
  for(let i=0;i<N;i++){
    const r = await p.evaluate(x=>window.__A.ev(x), `
      (()=>{ S.world = ${'${w}'.length} ? ${(0)} : 0; S.world = ${0}; S.idx = ${1};
        S.world = Math.floor(Math.random()*10); S.idx = Math.floor(Math.random()*12);
        startFight();
        const d=S.fight.d;
        return JSON.stringify({ name:d.name, slug:d.slug, boss:!!d.boss, kind:S.enc,
          talks:canSpeak(d),
          title:(document.querySelector('.scene .tag')||{}).textContent||'',
          cap:(ENC[S.enc].text(d)||''),
          line:(function(){ const e=document.getElementById('encSay'); return e? e.className : 'none'; })() });
      })()`);
    const o = JSON.parse(r);
    seen.kinds[o.kind]=(seen.kinds[o.kind]||0)+1;
    o.talks?seen.talker++:seen.beast++;
    /* the caption must name the monster */
    if(!o.cap.includes(o.name)) bad.push(`${o.name}: caption does not name it -> "${o.cap}"`);
    /* the title must match the kind of meeting */
    const wantTitle = {ambush:'Ambush!', spot:'You spot it first', path:'Blocked'}[o.kind];
    if(wantTitle && o.title.trim()!==wantTitle) bad.push(`${o.name}: ${o.kind} titled "${o.title}"`);
    if(o.kind==='boss' && !o.title.includes(o.name.replace(/^The /,''))) bad.push(`${o.name}: boss title "${o.title}"`);
  }
  /* now prove a beast never produces a speech bubble, over many draws */
  const speechByBeasts = await p.evaluate(x=>window.__A.ev(x), `
    (()=>{ let bad=[];
      for(let i=0;i<400;i++){
        S.world=Math.floor(Math.random()*10); S.idx=Math.floor(Math.random()*12);
        startFight();
        const d=S.fight.d, e=document.getElementById('encSay');
        const txt=(e&&e.textContent||'').trim();
        const cls=(e&&e.className)||'';
        if(!canSpeak(d) && txt && !/you/.test(cls)) bad.push(d.name+' said "'+txt+'"');
      }
      return JSON.stringify(bad.slice(0,5)); })()`);
  const sb = JSON.parse(speechByBeasts);
  await b.close(); srv.close();
  console.log(`${N} intros: ${seen.talker} can speak, ${seen.beast} cannot. kinds:`, seen.kinds);
  if(sb.length) console.log('BEASTS THAT SPOKE:', sb);
  if(bad.length){ console.log('\n' + bad.length + ' problems:'); bad.slice(0,10).forEach(x=>console.log('  ', x)); }
  console.log('js errors:', errs.length?errs.slice(0,3):'none');
  const okAll = !bad.length && !sb.length && !errs.length;
  console.log(okAll ? '\nEvery intro agrees with its monster.' : '\nFIX THE ABOVE.');
  process.exit(okAll?0:1);
})();
