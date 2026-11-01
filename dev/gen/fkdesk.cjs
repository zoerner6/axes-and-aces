/* Monster Farkle on a desktop: the monster fills the screen, nothing covers
   its face, and the dice stay readable.
     node dev/gen/fkdesk.cjs */
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = require('path').join(__dirname, '..', '..');
process.chdir(ROOT);
const { execFileSync } = require('child_process');
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
  const AUDIT=fs.readFileSync('dev/gen/audit.js','utf8');
  for(const [w,h] of [[1280,800],[1920,1080]]){
    const ctx=await b.newContext({viewport:{width:w,height:h}});
    const p=await ctx.newPage();
    const errs=[]; p.on('pageerror',e=>errs.push(e.message));
    await p.goto(base,{waitUntil:'load'}); await p.waitForTimeout(900);
    await p.evaluate(x=>window.__A.ev(x), `closePanel(); S.level=5; S.maxHp=800; S.hp=620; S.gold=48;
      S.eq={main:{type:'axe',tier:3},off:null,shield:{type:'shield',tier:2},helm:{type:'helm',tier:3},armor:{type:'armor',tier:2}};
      S.pots=['heal','iron']; S.world=0; S.idx=1; startFight();
      setTimeout(()=>{closePanel();busy=false;started=true;window.__FK.setFaces([1,5,3,3,6,2]);
        document.querySelector('[data-die="0"]').click();},1100);`);
    await p.waitForTimeout(3200);
    await p.addScriptTag({content:AUDIT});
    const r=await p.evaluate(l=>window.__AUDIT(l),`desktop@${w}x${h}`);
    await p.screenshot({path:`dev/gen/out/fk/desktop_${w}x${h}.png`});
    const bits=[];
    for(const k of ['overlaps','cropped','broken','clipped','offscreen','tiny','tapTargets'])
      if(r[k]&&r[k].length) bits.push(`${k}:${JSON.stringify(r[k]).slice(0,200)}`);
    if(errs.length) bits.push('jsErrors:'+JSON.stringify(errs.slice(0,2)));
    console.log(`${w}x${h}  ${bits.length?bits.join('  '):'clean'}`);
    await ctx.close();
  }
  await b.close(); srv.close();
})();
