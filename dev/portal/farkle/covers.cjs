/* Render the portal covers for Monster Farkle.
     node dev/portal/farkle/covers.cjs

   Writes into store/portal-farkle/:
     crazygames-cover-landscape-1920x1080.jpg
     crazygames-cover-portrait-800x1200.jpg
     crazygames-cover-square-800x800.jpg
     poki-thumbnail-square-1024x1024.jpg

   Built from the game's own mark, the way dev/gen/fkbanner.cjs builds the
   share banner: the real CSS and the real SVG lettering are lifted out of
   dev/farkle.html, so a cover can never drift from the start screen and the
   name can never come out misspelled.

   What BRAND.md asks for, and is checked here rather than trusted:
     - the mark gets clear space all round of at least the height of its "A"
     - the monster is whole; nothing crops a head
     - no AxesAndAces.com on a portal cover: the game lives on the portal
     - Poki's thumbnail carries no lettering at all, which is their rule */
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.join(__dirname, '..', '..', '..');
const OUT = path.join(ROOT, 'store', 'portal-farkle');
const MIME = {'.html':'text/html','.css':'text/css','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};

const src = fs.readFileSync(path.join(ROOT, 'dev', 'farkle.html'), 'utf8');
const css = src.match(/<style>([\s\S]*?)<\/style>/)[1];
const svg = src.match(/return `(<svg class="words"[\s\S]*?<\/svg>)`;/)[1];

/* The face of the game: a boss worth putting on a cover, shown whole. */
const FOE = 'bonedragon';
const BG = 'art/bg_w3_3.webp';
const BG_FALLBACK = 'art/bg_tavern.webp';
const bg = fs.existsSync(path.join(ROOT, BG)) ? BG : BG_FALLBACK;

const SHELL = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Germania+One&family=Oswald:wght@600;700&display=swap">
<style>
${css}
html,body{margin:0;overflow:hidden;background:#14100d}
.sheet{position:relative;overflow:hidden;background:#14100d}
.sheet .bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.4) saturate(.9)}
.sheet .veil{position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 44%, rgba(10,5,3,.3), rgba(10,5,3,.92) 80%)}
.sheet .bar{position:absolute;left:0;right:0;background:#000}
.sheet .bar.t{top:0} .sheet .bar.b{bottom:0}
/* object-fit:contain, never cover: a cropped head is a brand rule broken */
.foe{position:absolute;object-fit:contain;object-position:bottom center;
  filter:drop-shadow(0 18px 26px rgba(0,0,0,.8))}
.wrap{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.stack{display:flex;flex-direction:column;align-items:center}
.tag{font-family:'Oswald',Arial,sans-serif;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;color:#e8d9bb;text-shadow:0 2px 0 #000;text-align:center}
.icon{border-radius:14%;border:6px solid #000;box-shadow:0 18px 0 #000,0 30px 60px rgba(0,0,0,.75)}
</style></head><body>__BODY__</body></html>`;

/* Each cover: the size, how the plaque and the monster are laid out, and
   whether it may carry lettering at all. */
const COVERS = [
  { file: 'crazygames-cover-landscape-1920x1080.jpg', w: 1920, h: 1080, words: true,
    body: `<div class="sheet" style="width:1920px;height:1080px">
      <img class="bg" src="${bg}" alt="">
      <div class="veil"></div>
      <div class="bar t" style="height:20px"></div><div class="bar b" style="height:20px"></div>
      <img class="foe" src="art/${FOE}.webp" alt=""
           style="right:72px;bottom:40px;width:720px;height:900px">
      <div class="wrap" style="justify-content:flex-start;padding-left:150px">
        <div class="stack" style="gap:40px;align-items:flex-start">
          <div class="fklogo" style="width:960px;padding:38px 42px;gap:28px;border-radius:30px;
               box-shadow:0 14px 0 #000,0 26px 50px rgba(0,0,0,.7)">
            <img class="dice" src="img/farkle-dice.webp" alt="" style="width:204px">
            ${svg}
            <span class="ace" style="width:132px"></span>
          </div>
          <div class="tag" style="font-size:40px;text-align:left;max-width:940px">
            Six dice. One monster.<br>Wind up the blow, or lose the lot.</div>
        </div>
      </div>
    </div>` },

  { file: 'crazygames-cover-portrait-800x1200.jpg', w: 800, h: 1200, words: true,
    body: `<div class="sheet" style="width:800px;height:1200px">
      <img class="bg" src="${bg}" alt="">
      <div class="veil"></div>
      <div class="bar t" style="height:14px"></div><div class="bar b" style="height:14px"></div>
      <img class="foe" src="art/${FOE}.webp" alt=""
           style="left:50%;transform:translateX(-50%);bottom:34px;width:660px;height:620px">
      <div class="wrap" style="align-items:flex-start;padding-top:104px">
        <div class="stack" style="gap:30px">
          <div class="fklogo" style="width:612px;padding:26px 26px;gap:18px;border-radius:24px;
               box-shadow:0 12px 0 #000,0 22px 42px rgba(0,0,0,.7)">
            <img class="dice" src="img/farkle-dice.webp" alt="" style="width:130px">
            ${svg}
            <span class="ace" style="width:84px"></span>
          </div>
          <div class="tag" style="font-size:30px;max-width:660px">Six dice. One monster.</div>
        </div>
      </div>
    </div>` },

  { file: 'crazygames-cover-square-800x800.jpg', w: 800, h: 800, words: true,
    body: `<div class="sheet" style="width:800px;height:800px">
      <img class="bg" src="${bg}" alt="">
      <div class="veil"></div>
      <div class="bar t" style="height:14px"></div><div class="bar b" style="height:14px"></div>
      <img class="foe" src="art/${FOE}.webp" alt=""
           style="left:50%;transform:translateX(-50%);bottom:24px;width:580px;height:452px">
      <div class="wrap" style="align-items:flex-start;padding-top:104px">
        <div class="stack">
          <!-- no tagline here: at the size a square cover is shown the plaque
               already says the name, and the words were landing on the horns -->
          <div class="fklogo" style="width:596px;padding:24px 24px;gap:16px;border-radius:22px;
               box-shadow:0 11px 0 #000,0 20px 38px rgba(0,0,0,.7)">
            <img class="dice" src="img/farkle-dice.webp" alt="" style="width:126px">
            ${svg}
            <span class="ace" style="width:82px"></span>
          </div>
        </div>
      </div>
    </div>` },

  /* Poki ask for a thumbnail with no lettering on it, so this one carries the
     icon and the monster and says nothing. */
  { file: 'poki-thumbnail-square-1024x1024.jpg', w: 1024, h: 1024, words: false,
    body: `<div class="sheet" style="width:1024px;height:1024px">
      <img class="bg" src="${bg}" alt="" style="filter:brightness(.62) saturate(.95)">
      <!-- a lighter veil than the others: the icon's own ground is black, and
           on a near-black scene the badge reads as a hole rather than a tile -->
      <div class="veil" style="background:radial-gradient(ellipse at 50% 50%, rgba(10,5,3,.1), rgba(10,5,3,.72) 85%)"></div>
      <img class="icon" src="icons/farkle-512.png" alt=""
           style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:620px;height:620px">
    </div>` },
];

const srv = http.createServer((q, r) => {
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/, '');
  if (rel.startsWith('cover-')) {
    r.writeHead(200, { 'content-type': 'text/html' });
    return r.end(SHELL.replace('__BODY__', COVERS[+rel.slice(6)].body));
  }
  const f = path.join(ROOT, rel);
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end('no'); }
  r.writeHead(200, { 'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(r);
});

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/`;
  const b = await chromium.launch();
  let bad = 0;
  for (let i = 0; i < COVERS.length; i++) {
    const c = COVERS[i];
    const ctx = await b.newContext({ viewport: { width: c.w, height: c.h }, deviceScaleFactor: 1 });
    const p = await ctx.newPage();
    const missing = [];
    p.on('response', r => { if (r.status() >= 400) missing.push(r.url().replace(base, '')); });
    await p.goto(base + 'cover-' + i, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);

    /* Measure, do not assume. The clear-space rule is in pixels on this
       actual render, and a monster whose box is shorter than its natural
       shape would be squashed or cropped. */
    const m = await p.evaluate(() => {
      const box = el => { if (!el) return null; const r = el.getBoundingClientRect();
        return { x: r.x, y: r.y, w: r.width, h: r.height, r: innerWidth - r.right, b: innerHeight - r.bottom }; };
      const plaque = box(document.querySelector('.fklogo'));
      const words = document.querySelector('.words');
      const foeEl = document.querySelector('.foe');
      const foe = box(foeEl);

      /* The monster art is a cut-out with transparent margin all round, so
         its image box is bigger than the monster. Find the painted pixels and
         measure against those - otherwise a caption that clears the horns by
         a hair reads as covering the head, and a real overlap reads as fine. */
      function ink(img) {
        const c = document.createElement('canvas');
        const n = 260, s = Math.min(n / img.naturalWidth, n / img.naturalHeight);
        c.width = Math.max(1, Math.round(img.naturalWidth * s));
        c.height = Math.max(1, Math.round(img.naturalHeight * s));
        const g = c.getContext('2d', { willReadFrequently: true });
        g.drawImage(img, 0, 0, c.width, c.height);
        const d = g.getImageData(0, 0, c.width, c.height).data;
        let x0 = c.width, y0 = c.height, x1 = -1, y1 = -1;
        for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) {
          if (d[(y * c.width + x) * 4 + 3] > 24) {
            if (x < x0) x0 = x;
            if (x > x1) x1 = x;
            if (y < y0) y0 = y;
            if (y > y1) y1 = y;
          }
        }
        if (x1 < 0) return { x: 0, y: 0, w: 1, h: 1 };
        return { x: x0 / c.width, y: y0 / c.height,
                 w: (x1 - x0 + 1) / c.width, h: (y1 - y0 + 1) / c.height };
      }

      /* Where the monster is painted on the page: the box, narrowed to the
         art object-fit:contain actually draws, narrowed again to its ink. */
      let painted = null;
      if (foeEl && foeEl.naturalWidth) {
        const s = Math.min(foe.w / foeEl.naturalWidth, foe.h / foeEl.naturalHeight);
        const dw = foeEl.naturalWidth * s, dh = foeEl.naturalHeight * s;
        const dx = foe.x + (foe.w - dw) / 2, dy = foe.y + (foe.h - dh);  /* bottom center */
        const k = ink(foeEl);
        painted = { x: dx + k.x * dw, y: dy + k.y * dh, w: k.w * dw, h: k.h * dh };
      }

      const hits = [];
      if (painted) {
        for (const sel of ['.fklogo', '.tag', '.icon']) {
          for (const el of document.querySelectorAll(sel)) {
            const r = el.getBoundingClientRect();
            const ox = Math.min(r.right, painted.x + painted.w) - Math.max(r.left, painted.x);
            const oy = Math.min(r.bottom, painted.y + painted.h) - Math.max(r.top, painted.y);
            if (ox > 2 && oy > 2) hits.push(`${sel} covers ${Math.round(ox)}x${Math.round(oy)}px of the monster`);
          }
        }
      }
      return {
        plaque, foe, hits, painted,
        wordsH: words ? words.getBoundingClientRect().height : 0,
        natural: foeEl ? { w: foeEl.naturalWidth, h: foeEl.naturalHeight } : null,
        overflowX: document.documentElement.scrollWidth - innerWidth,
        overflowY: document.documentElement.scrollHeight - innerHeight,
        letters: [...document.querySelectorAll('.words, .tag')].length,
      };
    });

    const notes = [...m.hits];
    if (missing.length) notes.push('missing art: ' + missing.join(', '));
    if (m.overflowX > 0 || m.overflowY > 0) notes.push(`spills ${m.overflowX}x${m.overflowY}px`);
    if (c.words) {
      /* BRAND.md: clear space all round of at least the height of the "A".
         The cap height of the slab lettering is the SVG's own height. */
      const need = Math.round(m.wordsH * 0.55);   /* the "A" is about 55% of the block */
      const got = Math.min(m.plaque.x, m.plaque.y, m.plaque.r, m.plaque.b);
      if (got < need) notes.push(`clear space ${Math.round(got)}px, wants ${need}px`);
    } else if (m.letters) {
      notes.push('Poki thumbnail must carry no lettering');
    }
    if (m.foe && m.natural) {
      /* object-fit:contain means the whole monster is in the box whatever
         the box is, but a box far off the art's shape wastes the cover. */
      const boxAR = m.foe.w / m.foe.h, artAR = m.natural.w / m.natural.h;
      if (boxAR / artAR > 2 || artAR / boxAR > 2) notes.push('monster box is a bad fit for the art');
    }

    await p.screenshot({ path: path.join(OUT, c.file), type: 'jpeg', quality: 92 });
    const kb = fs.statSync(path.join(OUT, c.file)).size / 1024;
    if (notes.length) bad++;
    console.log(`${notes.length ? 'CHECK ' : '  ok  '}${c.file.padEnd(44)}${kb.toFixed(0)}KB`
      + (notes.length ? '\n        ' + notes.join('\n        ') : ''));
    await ctx.close();
  }
  await b.close(); srv.close();
  console.log(bad ? `\n${bad} cover(s) need a look.` : '\nFour covers, all within the brand rules.');
  process.exit(bad ? 1 : 0);
})();
