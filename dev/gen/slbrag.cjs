/* Do the brag cards hold together, and do their links land in the right game?

   node dev/gen/slbrag.cjs [--shot out.png]

   A brag card is the one thing from this game that strangers see, so what is
   checked is what a stranger would notice: that every kind renders, that the
   headline fits the space it is given instead of running off the side or
   being quietly dropped, that the address reads AxesAndAces.com the one way
   it is ever written, and that the page the share link points at redirects to
   solitaire.html rather than the front page. */
const { chromium } = require('playwright');
const { openGame } = require('./slopen.cjs');
const { execFileSync } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

/* A canvas that has drawn a file:// image is tainted, because file:// has an
   opaque origin, and toDataURL then throws - so a brag card cannot be checked
   off disk at all. Serving the repo over http for the length of the run gives
   the page the same-origin art it has everywhere it really runs. */
const TYPES = { '.html':'text/html', '.webp':'image/webp', '.png':'image/png', '.jpg':'image/jpeg',
                '.mp3':'audio/mpeg', '.mp4':'video/mp4', '.json':'application/json',
                '.js':'text/javascript', '.css':'text/css', '.webmanifest':'application/manifest+json' };
function serve(root){
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
      const f = path.join(root, rel);
      if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) {
        res.writeHead(404); return res.end('no');
      }
      res.writeHead(200, { 'content-type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve({ srv, port: srv.address().port }));
  });
}

const ROOT = path.resolve(__dirname, '..', '..');
execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
execFileSync('python', ['dev/gen/slbragpages.py'], { cwd: ROOT, stdio: 'pipe' });
const args = process.argv.slice(2);
const shotAt = args.includes('--shot') ? args[args.indexOf('--shot') + 1] : null;

const KINDS = ['run', 'boss', 'level', 'death', 'daily'];

(async () => {
  const { srv, port } = await serve(ROOT);
  const file = `http://127.0.0.1:${port}/solitaire.html`;
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  await p.route('**/music/**', r => r.abort());
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
  await p.goto(file, { waitUntil: 'load' });
  await p.waitForTimeout(400);
  await openGame(p);

  /* a hero with something to brag about */
  await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.level = 9; S.bestRun = 11; S.wins = 14; S.gold = 120;
    S.eq = { armor:{type:'armor',tier:3} };
    S.lastWin = { name:'Bandit Chief', slug:'bandit', boss:true };
    S.dailyResult = { date:'2026-11-02', score:4820, wins:4 };
  });

  let bad = 0;
  for (const kind of KINDS) {
    const m = await p.evaluate(async k => {
      const SOL = window.__SOL;
      const info = SOL.bragInfo(k);
      const c = await SOL.bragCard(info);
      /* measure the headline the way the card does, with the same font */
      const x = c.getContext('2d');
      x.font = '74px "Germania One", Georgia, serif';
      const wrap = (t, w) => { const out = []; let l = '';
        for (const word of String(t).split(' ')) { const n = l ? l + ' ' + word : word;
          if (x.measureText(n).width > w && l) { out.push(l); l = word; } else l = n; }
        if (l) out.push(l); return out; };
      const lines = wrap(info.title, 640);
      const widest = Math.max(...lines.map(l => x.measureText(l).width));
      x.font = '700 84px Oswald, Arial';
      const bigW = info.big ? x.measureText(info.big).width : 0;
      x.font = '64px "Germania One", Georgia, serif';
      const addrW = x.measureText('AxesAndAces.com').width;
      /* is anything actually painted? a blank card passes every other test */
      const px = x.getImageData(0, 0, c.width, c.height).data;
      let lit = 0;
      for (let i = 0; i < px.length; i += 4 * 97) if (px[i] + px[i + 1] + px[i + 2] > 120) lit++;
      /* did the pictures actually arrive? a card of text on an empty
         background passes every other check in here */
      const scene = await SOL.bragCard ? null : null;
      const gotBg = !!(await new Promise(res => { const im = new Image();
        im.onload = () => res(true); im.onerror = () => res(false); im.src = info.bg; }));
      const gotFig = !info.fig ? 'none' : !!(await new Promise(res => { const im = new Image();
        im.onload = () => res(true); im.onerror = () => res(false); im.src = info.fig; }));
      return { gotBg, gotFig, w:c.width, h:c.height, key:info.key, title:info.title, big:info.big,
               lines:lines.length, widest:Math.round(widest), bigW:Math.round(bigW),
               addrW:Math.round(addrW), lit, data:c.toDataURL('image/jpeg', .85).length };
    }, kind);

    const notes = [];
    if (m.w !== 1200 || m.h !== 630) { notes.push(`card is ${m.w}x${m.h}`); bad++; }
    if (m.lines > 2) { notes.push(`the headline needs ${m.lines} lines and only two are drawn: "${m.title}"`); bad++; }
    if (m.widest > 640) { notes.push(`a headline line is ${m.widest}px in a 640px space`); bad++; }
    if (m.big && m.bigW > 700) { notes.push(`"${m.big}" is ${m.bigW}px wide`); bad++; }
    if (56 + m.addrW > 1180) { notes.push(`the address is ${m.addrW}px and runs off the card`); bad++; }
    if (m.lit < 50) { notes.push(`the card looks blank (${m.lit} lit samples)`); bad++; }
    if (!m.gotBg) { notes.push('the scene behind it did not load'); bad++; }
    if (m.gotFig === false) { notes.push(`the figure ${m.key} wanted did not load`); bad++; }

    console.log(`  ${m.key.padEnd(11)} "${m.title}" / ${m.big}` +
      `  ${m.lines} line${m.lines === 1 ? '' : 's'}, widest ${m.widest}px, ${Math.round(m.data / 1024)}KB` +
      `, scene ${m.gotBg ? 'yes' : 'NO'}, figure ${m.gotFig}`);
    notes.forEach(n => console.log('      ** ' + n));
  }

  if (shotAt) {
    const d = await p.evaluate(async () => {
      const SOL = window.__SOL;
      const c = await SOL.bragCard(SOL.bragInfo('run'));
      return c.toDataURL('image/jpeg', .9);
    });
    fs.writeFileSync(shotAt, Buffer.from(d.split(',')[1], 'base64'));
    console.log(`  (a card written to ${shotAt})`);
  }

  /* the share pages */
  console.log('');
  for (const key of ['sol', 'sol_run', 'sol_boss', 'sol_level', 'sol_fallen', 'sol_daily']) {
    const f = path.join(ROOT, 'b', key + '.html');
    if (!fs.existsSync(f)) { console.log(`  ${key.padEnd(11)} *** MISSING ***`); bad++; continue; }
    const t = fs.readFileSync(f, 'utf8');
    const toGame = /location\.replace\("https:\/\/axesandaces\.com\/solitaire\.html"/.test(t);
    const canon = /rel="canonical" href="https:\/\/axesandaces\.com\/solitaire\.html"/.test(t);
    const ref = t.includes(`ref=${key}`);
    const ok = toGame && canon && ref;
    if (!ok) bad++;
    console.log(`  ${key.padEnd(11)} ${ok ? 'redirects to solitaire.html, with its own ref' :
      `*** game ${toGame} canonical ${canon} ref ${ref} ***`}`);
  }

  console.log(errs.length ? `\nERRORS: ${[...new Set(errs)].join(' | ')}` : '\nno page errors');
  await b.close();
  srv.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
