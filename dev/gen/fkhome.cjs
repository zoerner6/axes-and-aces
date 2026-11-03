/* Can you actually get back out of Monster Farkle?
   A link that exists is not a link that works, so this clicks both of them and
   checks where the browser lands.
     node dev/gen/fkhome.cjs */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
execFileSync('python', ['dev/gen/harness.py', 'dev/farkle.html', 'farkletest.html'], { stdio: 'inherit' });
const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
const srv = http.createServer((q, r) => {
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/, '') || 'farkletest.html';
  const f = path.join(ROOT, rel);
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end('no'); }
  r.writeHead(200, { 'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(r);
});
(async () => {
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const b = await chromium.launch();
  let bad = 0;
  for (const [w, h] of [[390, 844], [320, 568]]) {
    for (const [how, open, sel] of [
      /* a panel covers the whole screen, so the bar is only reachable with
         none open - which is the normal state once you are playing */
      ['the mark in the bar', 'closePanel();', 'a.brand[href="index.html"]'],
      ['the menu row', 'closePanel(); menuPanel();', '#overlay a.buy[href="index.html"]'],
    ]) {
      const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
      const p = await ctx.newPage();
      await p.goto(base, { waitUntil: 'load' });
      await p.waitForTimeout(700);
      if (open) await p.evaluate(x => window.__A.ev(x), open);
      await p.waitForTimeout(350);
      const el = await p.$(sel);
      if (!el) { console.log(`${w}x${h}  ${how.padEnd(20)} NOT FOUND`); bad++; await ctx.close(); continue; }
      const box = await el.boundingBox();
      await el.click();
      await p.waitForTimeout(900);
      const landed = /index\.html$/.test(p.url());
      const big = box && box.height >= 44;
      console.log(`${w}x${h}  ${how.padEnd(20)} tap ${Math.round(box.width)}x${Math.round(box.height)} ${big ? 'ok' : 'UNDER 44'}  ->  ${landed ? 'home' : 'STAYED PUT (' + p.url().split('/').pop() + ')'}`);
      if (!landed || !big) bad++;
      await ctx.close();
    }
  }
  await b.close(); srv.close();
  console.log(bad ? `\n${bad} problem(s).` : '\nBoth ways out work, at both sizes.');
  process.exit(bad ? 1 : 0);
})();
