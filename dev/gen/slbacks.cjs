/* Do all ten deck backs read at 320px, and is every face still identical?

   node dev/gen/slbacks.cjs

   dev/plans/solitaire.md, step 16: the back is the one thing per world the
   cards are allowed to change, and the faces never are. So this checks both
   halves - that each back stands off the table clearly enough to read as a
   card at the smallest size the game supports, and that nothing about a face
   differs between world one and world ten. */
const { chromium } = require('playwright');
const { openGame } = require('./slopen.cjs');
const { execFileSync } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const fs = require('fs');
const SHOTS = path.join(ROOT, 'dev', 'gen', 'out', 'slbacks');
fs.mkdirSync(SHOTS, { recursive: true });

/* WHAT "THE TABLE" IS. This compared each back with body's background-color,
   which was right while the page was one flat soot colour. The table is a
   felt now - a lamp-lit gradient, bright in the middle where the cards sit
   and near black at the rail - and background-color is only its darkest
   edge, a colour no card ever sits on. Measured against that, four worlds
   failed the 1.5 floor.

   So the floor stays where it was and the measurement gets honest: hide the
   cards, photograph the felt exactly where a face-down card sits, average
   it, and compare the back with THAT. Both boards are checked, because the
   two lay their backs out in different places on the gradient. */
const feltUnder = async (p, sel, name) => {
  /* on screen first: a full-page capture resizes the window, which lays the
     board out again somewhere else, so the photo would miss the card */
  const box = await p.evaluate(s => {
    const e = document.querySelector(s);
    if (!e) return null;
    e.scrollIntoView({ block: 'center' });
    const r = e.getBoundingClientRect();
    return { x: r.left, y: r.top, width: r.width, height: r.height };
  }, sel);
  if (!box || box.width < 2 || box.height < 2) return null;
  /* hide the cards with a tag of our own, and take back only that tag - the
     first version removed "the last style on the page", which is the GAME'S
     stylesheet, and every world after the first was measured unstyled */
  await p.evaluate(() => {
    const t = document.createElement('style');
    t.id = 'slbacks-hide';
    t.textContent = '#board .pk,#board .stockn{visibility:hidden!important}';
    document.head.appendChild(t);
  });
  const file = path.join(SHOTS, name);
  await p.screenshot({ path: file, clip: box });
  await p.evaluate(() => document.getElementById('slbacks-hide').remove());
  return file;
};
/* the card as it is actually drawn, for measuring its margin */
const cardPhoto = async (p, sel, name) => {
  const box = await p.evaluate(s => {
    const e = document.querySelector(s);
    if (!e) return null;
    e.scrollIntoView({ block: 'center' });
    const r = e.getBoundingClientRect();
    return { x: r.left, y: r.top, width: r.width, height: r.height };
  }, sel);
  if (!box || box.width < 2 || box.height < 2) return null;
  const file = path.join(SHOTS, name);
  await p.screenshot({ path: file, clip: box });
  return file;
};
execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const file = path.join(ROOT, 'solitaire.html').replace(/\\/g, '/');

/* relative luminance, so "reads against the table" is a number and not a look */
const lum = (r, g, b) => {
  const f = c => { c /= 255; return c <= .03928 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4); };
  return .2126 * f(r) + .7152 * f(g) + .0722 * f(b);
};
const ratio = (a, b) => { const [x, y] = [lum(...a), lum(...b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
const parse = s => (s.match(/\d+/g) || [0, 0, 0]).slice(0, 3).map(Number);

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 320, height: 568 }, deviceScaleFactor: 2,
    isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  await p.route('**/vid/**', r => r.abort());
    await p.route('**/music/**', r => r.abort());   /* not what this one is measuring */
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
  await p.goto('file://' + file, { waitUntil: 'load' });
  await p.waitForTimeout(400);
  /* THIS TOOL TESTS THE PEAKS BOARD, so put the page on it. Tri-Peaks used
     to be the only board and dealRound used to deal it; it is an unlock now
     and a fresh hero is on Klondike, so every deal below came back as columns
     and every R.tableau in here was undefined. dev/gen/klgear.cjs asks the
     same questions of Klondike. */
  await p.evaluate(() => { window.__SOL.S.board = 'peaks'; });
    await openGame(p);          /* the game opens on its story now */

  let bad = 0;
  const faces = [], rows = [];

  for (let w = 0; w < 10; w++) {
    const m = await p.evaluate(wi => {
      const SOL = window.__SOL;
      document.body.className = 'w' + wi;
      /* a board with a peak face down, so there are backs on the table */
      SOL.R = SOL.dealRound({ hidden: [1] });
      SOL.R.tableau[18].r = 7; SOL.R.tableau[18].s = 0;   /* a fixed 7 of spades */
      SOL.render();
      const back = document.querySelector('.peaks .pk.down');
      /* the same card every time, and a known suit, so the only thing that
         can differ between worlds is the world */
      const face = document.querySelector('.peaks .pk[data-i="18"]:not(.down)')
                || document.querySelector('.peaks .pk:not(.down)');
      /* the back colors are set on body, which is what carries the world
         class - reading them off :root gets nothing at all */
      const cs = back ? getComputedStyle(back) : getComputedStyle(document.body);
      const bodyBg = getComputedStyle(document.body).backgroundColor;
      const fs = face ? getComputedStyle(face) : null;
      const corner = face ? getComputedStyle(face.querySelector('.cn')) : null;
      return {
        a: cs.getPropertyValue('--back-a').trim(),
        b: cs.getPropertyValue('--back-b').trim(),
        bodyBg,
        backBox: back ? (() => { const r = back.getBoundingClientRect(); return Math.round(r.width) + 'x' + Math.round(r.height); })() : null,
        backs: document.querySelectorAll('.peaks .pk.down').length,
        /* the whole of what a face is: its paper, its border and its corner
           type. The ink is left out on purpose - that is the card's suit, not
           the world, and comparing it across worlds compared a red card with
           a black one and called the difference a bug. */
        face: fs ? [fs.backgroundColor, fs.borderTopWidth, fs.borderRadius,
                    corner.fontSize, corner.fontFamily, corner.fontWeight].join(' | ') : ''
      };
    }, w);

    faces.push(m.face);
    const peaksCard = await cardPhoto(p, '.peaks .pk.down', `card-peaks-w${w + 1}.png`);
    const peaksShot = await feltUnder(p, '.peaks .pk.down', `felt-peaks-w${w + 1}.png`);

    /* and the board everybody starts on: Klondike's deck is a whole back */
    await p.evaluate(wi => {
      const SOL = window.__SOL;
      document.body.className = 'w' + wi;
      SOL.R = SOL.dealRound({ kind: 'klondike' });
      SOL.render();
    }, w);
    const klCard = await cardPhoto(p, '[data-act="draw"]', `card-klondike-w${w + 1}.png`);
    const klShot = await feltUnder(p, '[data-act="draw"]', `felt-klondike-w${w + 1}.png`);
    rows.push({ w, m, peaksShot, klShot, peaksCard, klCard });
  }

  /* average each photograph of the felt in one Python call */
  /* The felt is the whole photograph averaged. The card's margin is a strip
     of its own photograph: inside the 2.5px outline and before the thin dark
     line that frames the pattern - 3 to 5 CSS pixels in, which at
     deviceScaleFactor 2 is rows 6 to 10, across the middle half. */
  const shots = rows.flatMap(r => [r.peaksShot, r.klShot]).filter(Boolean);
  const cards = rows.flatMap(r => [r.peaksCard, r.klCard]).filter(Boolean);
  const avg = JSON.parse(execFileSync('python', ['-I', '-c', `
import json, sys
from PIL import Image, ImageStat
n = int(sys.argv[1]); files = sys.argv[2:]
out = {}
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB')
    if i >= n:
        w, h = im.size
        im = im.crop((w // 4, 6, w - w // 4, 11))
    out[f] = [round(c) for c in ImageStat.Stat(im).mean]
print(json.dumps(out))
`, String(shots.length), ...shots, ...cards], { encoding: 'utf8' }));

  const hex = s => s.startsWith('#')
    ? [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16))
    : parse(s);
  const css = c => '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');
  /* WHAT HAS TO STAND OFF THE TABLE IS THE CARD'S EDGE. Each back now sits
     inside a cream margin, the way a real deck does, and that margin is the
     thing a player sees separate the card from the felt - so that is what is
     held to a floor, and the floor went UP, from 1.5 to 3:1, the contrast
     the web's own guidance asks of any shape that has to be seen. The fill
     against the felt is still printed, as information: it is the world's
     colour, and it is allowed to be close to the table now that it is framed. */
  console.log('margin against the felt under it, floor 3:1 - fill shown for reference\n');
  for (const { w, m, peaksShot, klShot, peaksCard, klCard } of rows) {
    const back = hex(m.a);
    const mp = peaksShot && peaksCard ? ratio(avg[peaksCard], avg[peaksShot]) : 0;
    const mk = klShot && klCard ? ratio(avg[klCard], avg[klShot]) : 0;
    const fp = peaksShot ? ratio(back, avg[peaksShot]) : 0;
    const fk = klShot ? ratio(back, avg[klShot]) : 0;
    const ok = m.backs > 0 && mp >= 3 && mk >= 3;
    if (!ok) bad++;
    console.log(`world ${String(w + 1).padStart(2)}  back ${m.a}  ` +
      `peaks: margin ${mp.toFixed(2)}:1 (fill ${fp.toFixed(2)})   ` +
      `klondike deck: margin ${mk.toFixed(2)}:1 (fill ${fk.toFixed(2)})  ` +
      `${ok ? '' : '*** THE CARD DOES NOT STAND OFF THE TABLE ***'}`);
  }

  const sameFace = faces.every(f => f === faces[0]);
  if (!sameFace) bad++;
  console.log(`\nevery face identical across the ten worlds: ${sameFace ? 'yes' : 'NO'}`);
  if (!sameFace) [...new Set(faces)].forEach(f => console.log('   ' + f));
  console.log(errs.length ? `ERRORS: ${[...new Set(errs)].join(' | ')}` : 'no page errors');

  await b.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
