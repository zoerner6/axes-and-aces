/* Look at the Monster Farkle card on the front page, phone and desktop.
     node dev/gen/fkfront.cjs */
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
const srv = http.createServer((q,r)=>{
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'') || 'index.html';
  const f = path.join(ROOT, rel);
  if(!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ r.writeHead(404); return r.end('no'); }
  r.writeHead(200,{'content-type':MIME[path.extname(f).toLowerCase()]||'application/octet-stream'});
  fs.createReadStream(f).pipe(r);
});
(async()=>{
  await new Promise(z=>srv.listen(0,'127.0.0.1',z));
  const base=`http://127.0.0.1:${srv.address().port}/index.html`;
  const AUDIT=fs.readFileSync('dev/gen/audit.js','utf8');
  const b=await chromium.launch();
  fs.mkdirSync('dev/gen/out/fk',{recursive:true});
  for(const [w,h,tag] of [[390,844,'phone'],[1280,900,'desktop']]){
    const ctx=await b.newContext({viewport:{width:w,height:h},isMobile:w<700,hasTouch:w<700});
    const p=await ctx.newPage();
    const errs=[]; p.on('pageerror',e=>errs.push(e.message));
    await p.goto(base,{waitUntil:'load'});
    await p.waitForTimeout(900);
    const card = await p.$('.farkle-cta');
    if(!card){ console.log(`${tag}: FARKLE CARD NOT FOUND`); await ctx.close(); continue; }
    await card.scrollIntoViewIfNeeded();
    await p.waitForTimeout(900);
    await p.evaluate(()=>document.querySelectorAll('.rv').forEach(e=>e.classList.add('in','seen','show')));
    await p.waitForTimeout(400);
    await card.screenshot({path:`dev/gen/out/fk/front_${tag}.png`});
    await p.addScriptTag({content:AUDIT});
    const r=await p.evaluate(l=>window.__AUDIT(l),`front@${tag}`);
    const bits=[];
    for(const k of ['overlaps','cropped','broken','clipped','offscreen','tiny','tapTargets'])
      if(r[k]&&r[k].length) bits.push(`${k}:${JSON.stringify(r[k]).slice(0,180)}`);
    if(errs.length) bits.push('jsErrors:'+JSON.stringify(errs.slice(0,2)));
    const href = await p.evaluate(()=>document.querySelector('.farkle-cta .btn').getAttribute('href'));
    console.log(`${tag}  link=${href}  ${bits.length?bits.join('  '):'clean'}`);
    await ctx.close();
  }
  await b.close(); srv.close();
})();
