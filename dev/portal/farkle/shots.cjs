/* Screenshots of the real package, for the store listings.
     node dev/portal/farkle/shots.cjs [poki|crazygames]

   Shot from dist/farkle-<portal>/, not from the dev page, so what a reviewer
   sees is what the package actually does. Writes into store/portal-farkle/.

   Each shot is checked before it is kept: nothing clipped, nothing spilling,
   no text on text. A screenshot of a broken frame is worse than no
   screenshot, because it goes in front of a reviewer. */
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const PORTAL = process.argv[2] || 'crazygames';
const ROOT = path.join(__dirname, '..', '..', '..');
const DIST = path.join(ROOT, 'dist', 'farkle-' + PORTAL);
const OUT = path.join(ROOT, 'store', 'portal-farkle');
if (!fs.existsSync(DIST)) { console.error('No package at ' + DIST); process.exit(2); }

const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json',
  '.jpg':'image/jpeg','.woff2':'font/woff2'};

const tap = (pg, sel) => pg.evaluate(s => {
  const el = document.querySelector(s);
  if (!el || el.disabled) return false;
  el.click(); return true;
}, sel);

/* Get to a fight with dice on the table and a wind worth looking at. */
async function intoAFight(p, { boss = false, world = 0, idx = 0 } = {}) {
  await p.evaluate(({ boss, world, idx }) => {
    const FK = window.__FK;
    FK.S.world = world;
    FK.S.idx = boss ? idx + 2 : idx;      /* third fight of an area is the boss */
    FK.S.level = 6 + world * 8;
    FK.S.hp = FK.S.maxHp;
    FK.S.introBeat = 9; FK.S.endBeat = 9; /* the opening scenes are already read */
    FK.startFight();
  }, { boss, world, idx });
  await p.waitForTimeout(1400);
}

/* Roll and keep until the wind is worth a screenshot. */
async function windUp(p, want = 650) {
  await tap(p, '#overlay:not([hidden]) [data-act="fight"]');
  await p.waitForTimeout(600);
  for (let i = 0; i < 8; i++) {
    const rolled = await tap(p, '#rollBtn');
    if (!rolled) break;
    await p.waitForTimeout(700);
    const state = await p.evaluate(() => {
      const FK = window.__FK, roll = FK.rollIdx();
      if (!roll.length) return { wind: 0, done: true };
      const best = FK.bestSplit(FK.facesOf(roll));
      if (!best.score) return { wind: 0, done: true };   /* farkled: start over */
      best.keep.forEach(k => {
        const el = document.querySelector(`[data-die="${roll[k]}"]`);
        if (el && !el.disabled) el.click();
      });
      return { wind: +document.getElementById('windNum').textContent.replace(/,/g, ''), done: false };
    });
    if (state.done) return false;
    if (state.wind >= want) return true;
  }
  return true;
}

const SHOTS = [
  { file: 'screenshot-1-fight.png', w: 1920, h: 1080, scale: 1,
    async go(p) { await intoAFight(p, { world: 2, idx: 0 }); await windUp(p, 600); } },
  { file: 'screenshot-2-boss.png', w: 1920, h: 1080, scale: 1,
    async go(p) { await intoAFight(p, { boss: true, world: 4, idx: 3 }); await p.waitForTimeout(1600); } },
  { file: 'screenshot-3-scoring.png', w: 1920, h: 1080, scale: 1,
    async go(p) {
      await intoAFight(p, { world: 1, idx: 1 });
      await tap(p, '#overlay:not([hidden]) [data-act="fight"]');
      await p.waitForTimeout(500);
      await p.evaluate(() => window.__FK.openPanel('')); /* cleared, then the real panel */
      await tap(p, '[data-act="guide"]');
      await p.waitForTimeout(900);
    } },
  { file: 'screenshot-phone-1-fight.png', w: 540, h: 960, scale: 2,
    async go(p) { await intoAFight(p, { world: 3, idx: 0 }); await windUp(p, 500); } },
  { file: 'screenshot-phone-2-boss.png', w: 540, h: 960, scale: 2,
    async go(p) { await intoAFight(p, { boss: true, world: 6, idx: 6 }); await p.waitForTimeout(1600); } },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const srv = http.createServer((q, r) => {
    const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
    const f = path.join(DIST, rel);
    if (!f.startsWith(DIST) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end('no'); }
    r.writeHead(200, { 'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(r);
  });
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/`;
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  let bad = 0;

  for (const s of SHOTS) {
    const phone = s.w < 700;
    const ctx = await b.newContext({ viewport: { width: s.w, height: s.h },
      deviceScaleFactor: s.scale, isMobile: phone, hasTouch: phone, reducedMotion: 'reduce' });
    const p = await ctx.newPage();
    await p.goto(base, { waitUntil: 'load' });
    await p.waitForTimeout(2000);
    /* The portal SDK's loading panel never clears on a local server, and it
       would be in every shot: take it out of the picture, not out of the
       package - the package is what gets submitted and it keeps the SDK.
       Name the game's own elements and leave everything of its alone; a
       blanket "remove the rest" took the stylesheet with it and every shot
       came out unstyled. */
    const KEPT = await p.evaluate(() => {
      const mine = new Set(['app', 'overlay', 'fx']);
      const kept = [], gone = [];
      for (const el of [...document.body.children]) {
        if (mine.has(el.id) || el.tagName === 'SCRIPT' || el.tagName === 'STYLE'
            || el.tagName === 'LINK') { kept.push(el.tagName + '#' + el.id); continue; }
        gone.push(el.tagName + '#' + el.id); el.remove();
      }
      return { kept, gone };
    });
    if (!KEPT.kept.some(k => k.endsWith('#app'))) {
      console.log('  the game is not on the page; shots would be empty');
      process.exit(1);
    }
    for (let i = 0; i < 12; i++) {
      if (!await tap(p, '#overlay:not([hidden]) [data-act="storyNext"]')) break;
      await p.waitForTimeout(400);
    }
    await s.go(p);
    await p.waitForTimeout(500);

    const m = await p.evaluate(() => {
      const d = document.documentElement, panel = document.getElementById('panel');
      const clipped = [];
      for (const el of document.querySelectorAll('#app *, #panel *')) {
        if (!el.offsetParent && el.tagName !== 'BODY') continue;
        if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow === 'hidden'
            && el.childElementCount === 0 && el.textContent.trim()) {
          clipped.push((el.className || el.tagName) + ': ' + el.textContent.trim().slice(0, 28));
        }
      }
      return {
        pageScroll: Math.max(0, d.scrollHeight - d.clientHeight, d.scrollWidth - d.clientWidth),
        panelScroll: panel && !document.getElementById('overlay').hidden
          ? Math.max(0, panel.scrollHeight - panel.clientHeight) : 0,
        clipped: clipped.slice(0, 4),
      };
    });

    await p.screenshot({ path: path.join(OUT, s.file) });
    const notes = [];
    if (m.pageScroll > 0) notes.push(`page spills ${m.pageScroll}px`);
    if (m.panelScroll > 0) notes.push(`panel needs ${m.panelScroll}px of scroll`);
    if (m.clipped.length) notes.push('clipped text: ' + m.clipped.join(' | '));
    const kb = fs.statSync(path.join(OUT, s.file)).size / 1024;
    if (notes.length) bad++;
    console.log(`${notes.length ? 'CHECK ' : '  ok  '}${s.file.padEnd(32)}${s.w * s.scale}x${s.h * s.scale}  ${kb.toFixed(0)}KB`
      + (notes.length ? '\n        ' + notes.join('\n        ') : ''));
    await ctx.close();
  }

  await b.close(); srv.close();
  console.log(bad ? `\n${bad} shot(s) need a look.` : `\n${SHOTS.length} screenshots, all clean.`);
  process.exit(bad ? 1 : 0);
})();
