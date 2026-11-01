/* Take a look at one screen of Monster Farkle at every phone size, and run the
   screen auditor on it.
     node dev/gen/fkshot.cjs <name> "<js to run>" [waitMs]
   Clips are let through, so a monster that is supposed to be moving is. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
const name = process.argv[2] || 'fight';
const js = process.argv[3] || '';
const waitMs = +(process.argv[4] || 2600);
execFileSync('python', ['dev/gen/harness.py','dev/farkle.html','farkletest.html'], {stdio:'inherit'});
const srv = http.createServer((q,r)=>{
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'') || 'farkletest.html';
  const f = path.join(ROOT, rel);
  if(!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ r.writeHead(404); return r.end('no'); }
  r.writeHead(200, {'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream'});
  fs.createReadStream(f).pipe(r);
});
(async () => {
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const AUDIT = fs.readFileSync('dev/gen/audit.js','utf8');
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  fs.mkdirSync('dev/gen/out/fk', {recursive:true});
  for(const [w,h] of [[390,844],[375,667],[360,740],[320,568]]){
    const ctx = await b.newContext({viewport:{width:w,height:h}, deviceScaleFactor:2, isMobile:true, hasTouch:true});
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    p.on('console', m => { if(m.type()==='error') errs.push(m.text().slice(0,160)); });
    await p.goto(base, {waitUntil:'load'});
    await p.waitForTimeout(900);
    if(js) await p.evaluate(x => window.__A.ev(x), js);
    await p.waitForTimeout(waitMs);
    await p.addScriptTag({content: AUDIT});
    const r = await p.evaluate(l => window.__AUDIT(l), `${name}@${w}x${h}`);
    await p.screenshot({path:`dev/gen/out/fk/${name}_${w}x${h}.png`});
    const bits = [];
    for(const k of ['overlaps','cropped','broken','clipped','offscreen','tiny','tapTargets'])
      if(r[k] && r[k].length) bits.push(`${k}:${JSON.stringify(r[k]).slice(0,220)}`);
    /* No popup may need scrolling to reach its main button. The screen auditor
       does not know about this, because it looks at elements and this is about
       a box being taller than the room it has. */
    const over = await p.evaluate(() => {
      const ov = document.getElementById('overlay');
      if(!ov || ov.hidden) return null;
      const el = document.getElementById('panel');
      const spill = el.scrollHeight - el.clientHeight;
      if(spill <= 1) return null;
      /* the main button is the last .btn.big that is a direct child of the
         panel - not a .buy row inside a list, which :last-of-type would find */
      const big = [...el.children].filter(c => c.classList.contains('btn') && c.classList.contains('big'));
      const last = big[big.length - 1];
      return { spill, mainButtonBelowTheFold: last ? Math.round(last.getBoundingClientRect().bottom - el.getBoundingClientRect().bottom) : null };
    });
    if(over) bits.push(`panelScrolls:${JSON.stringify(over)}`);
    if(errs.length) bits.push('jsErrors:' + JSON.stringify(errs.slice(0,3)));
    console.log(`${w}x${h}  ${bits.length ? bits.join('  ') : 'clean'}`);
    await ctx.close();
  }
  await b.close(); srv.close();
})();
