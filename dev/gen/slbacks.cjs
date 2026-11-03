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
  const faces = [];

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

    const hex = s => s.startsWith('#')
      ? [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16))
      : parse(s);
    const r = ratio(hex(m.a), parse(m.bodyBg));
    const ok = m.backs > 0 && r >= 1.5;
    if (!ok) bad++;
    faces.push(m.face);
    console.log(`world ${String(w + 1).padStart(2)}  back ${m.a} over ${m.b}  ` +
      `${m.backs} face down at ${m.backBox}  stands off the table ${r.toFixed(2)}:1  ` +
      `${ok ? '' : '*** TOO CLOSE TO THE TABLE ***'}`);
  }

  const sameFace = faces.every(f => f === faces[0]);
  if (!sameFace) bad++;
  console.log(`\nevery face identical across the ten worlds: ${sameFace ? 'yes' : 'NO'}`);
  if (!sameFace) [...new Set(faces)].forEach(f => console.log('   ' + f));
  console.log(errs.length ? `ERRORS: ${[...new Set(errs)].join(' | ')}` : 'no page errors');

  await b.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
