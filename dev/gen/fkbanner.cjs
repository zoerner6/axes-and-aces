/* Render the Monster Farkle sharing banner, b/farkle.jpg (1200x630).
     node dev/gen/fkbanner.cjs

   This is the picture Facebook fetches when somebody posts a link to the
   game, so it cannot be the Axes & Aces banner: BRAND.md is explicit that the
   Axes & Aces word logo does not go on a product that is not Axes & Aces.

   It is drawn from the game's own mark rather than a separate design, by
   loading the real CSS and the real SVG lettering out of dev/farkle.html, so
   the banner can never drift from what the start screen shows. */
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
const MIME = {'.html':'text/html','.css':'text/css','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};

const src = fs.readFileSync('dev/farkle.html', 'utf8');
/* the page's own styles, so the plaque here is the plaque there */
const css = src.match(/<style>([\s\S]*?)<\/style>/)[1];
/* the page's own lettering, lifted whole */
const svg = src.match(/return `(<svg class="words"[\s\S]*?<\/svg>)`;/)[1];

const page = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Germania+One&family=Oswald:wght@600;700&display=swap">
<style>
${css}
html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{display:grid;place-items:center;background:#14100d}
.sheet{position:relative;width:1200px;height:630px;overflow:hidden}
.sheet .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.42) saturate(.9)}
.sheet .veil{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 42%, rgba(10,5,3,.35), rgba(10,5,3,.9) 78%)}
.sheet .bar{position:absolute;left:0;right:0;height:14px;background:#000}
.sheet .bar.t{top:0} .sheet .bar.b{bottom:0}
.wrap{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px}
.fklogo{width:900px;padding:34px 38px;gap:26px;border-radius:26px;box-shadow:0 12px 0 #000,0 22px 44px rgba(0,0,0,.7)}
.fklogo .dice{width:190px}
.fklogo .ace{width:124px}
.tag{font-family:'Oswald',Arial,sans-serif;font-weight:600;font-size:30px;letter-spacing:.1em;
  text-transform:uppercase;color:#e8d9bb;text-shadow:0 2px 0 #000}
.cta{display:flex;align-items:baseline;gap:14px}
.cta i{font-style:normal;font-family:'Germania One',Georgia,serif;font-size:34px;color:#ffd35c;
  -webkit-text-stroke:6px #000;paint-order:stroke fill}
.cta b{font-family:'Germania One',Georgia,serif;font-weight:400;font-size:60px;color:#fff;
  -webkit-text-stroke:9px #000;paint-order:stroke fill}
.made{position:absolute;right:34px;bottom:30px;display:flex;align-items:center;gap:10px;
  font-family:'Oswald',Arial,sans-serif;font-weight:600;font-size:19px;letter-spacing:.09em;
  text-transform:uppercase;color:#c7b28c;opacity:.92}
.made img{width:34px;height:34px;border-radius:7px;border:2px solid #000}
</style></head><body>
<div class="sheet">
  <img class="bg" src="art/bg_tavern.webp" alt="">
  <div class="veil"></div>
  <div class="bar t"></div><div class="bar b"></div>
  <div class="wrap">
    <div class="fklogo">
      <img class="dice" src="img/farkle-dice.webp" alt="">
      ${svg}
      <span class="ace"></span>
    </div>
    <div class="tag">Six dice. One monster.</div>
    <div class="cta"><i>Play free at</i><b>AxesAndAces.com</b></div>
  </div>
  <div class="made"><img src="img/emblem-64.webp" alt="">An Axes &amp; Aces game</div>
</div></body></html>`;

const srv = http.createServer((q, r) => {
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/, '');
  if (!rel || rel === 'banner.html') { r.writeHead(200, {'content-type':'text/html'}); return r.end(page); }
  const f = path.join(ROOT, rel);
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { r.writeHead(404); return r.end('no'); }
  r.writeHead(200, {'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream'});
  fs.createReadStream(f).pipe(r);
});
(async () => {
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto(`http://127.0.0.1:${srv.address().port}/banner.html`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(700);
  fs.mkdirSync('b', { recursive: true });
  await p.screenshot({ path: 'b/farkle.jpg', type: 'jpeg', quality: 90 });
  await b.close(); srv.close();
  console.log(`b/farkle.jpg  ${fs.statSync('b/farkle.jpg').size.toLocaleString()} bytes`);
})();
