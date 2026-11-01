/* Does the daily challenge really give everybody the same day?
   Two clean browsers, same day, must see the same monsters and the same dice.
     node dev/gen/fkdaily.cjs */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
execFileSync('python', ['dev/gen/harness.py','dev/farkle.html','farkletest.html'], {stdio:'inherit'});
const srv = http.createServer((q,r)=>{
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'') || 'farkletest.html';
  const f = path.join(ROOT, rel);
  if(!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ r.writeHead(404); return r.end('no'); }
  r.writeHead(200, {'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream'});
  fs.createReadStream(f).pipe(r);
});
async function runOne(b, base){
  /* a brand new browser each time: no saves, no stored name */
  const ctx = await b.newContext({viewport:{width:390,height:844}, isMobile:true, hasTouch:true, reducedMotion:'reduce'});
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(base, {waitUntil:'load'});
  await p.waitForTimeout(600);
  await p.evaluate(x => window.__A.ev(x), 'startDaily();');
  await p.waitForTimeout(200);
  await p.evaluate(x => window.__A.ev(x), 'closePanel(); S.idx=0; startFight();');
  await p.waitForTimeout(600);
  const seen = [];
  for(let fight = 0; fight < 3; fight++){
    seen.push('monster:' + await p.evaluate(() => window.__FK.S.fight.d.name));
    for(let r = 0; r < 3; r++){
      await p.evaluate(x => window.__A.ev(x), 'rolling=false; busy=false; started=true;');
      await p.evaluate(x => window.__A.ev(x), 'rollDice();');
      await p.waitForTimeout(140);
      seen.push(await p.evaluate(() => window.__FK.D.map(d => d.f).join('')));
    }
    await p.evaluate(x => window.__A.ev(x), 'S.daily.n++; S.idx=S.daily.n; startFight();');
    await p.waitForTimeout(400);
  }
  await ctx.close();
  return { seen, errs };
}
(async () => {
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const b = await chromium.launch();
  const a = await runOne(b, base);
  const c = await runOne(b, base);
  await b.close(); srv.close();
  const same = JSON.stringify(a.seen) === JSON.stringify(c.seen);
  console.log('browser one:', a.seen.join('  '));
  console.log('browser two:', c.seen.join('  '));
  console.log(same ? '\nSAME DAY, SAME DICE. The daily challenge is fair.'
                   : '\nTHEY DIFFER - the daily is not seeded properly.');
  console.log('js errors:', a.errs.concat(c.errs).length ? a.errs.concat(c.errs) : 'none');
  process.exit(same ? 0 : 1);
})();
