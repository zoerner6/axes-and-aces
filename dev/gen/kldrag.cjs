/* Does dragging a card actually move it - with a mouse, and with a finger?
     node dev/gen/kldrag.cjs

   Josh played Monster Solitaire and did not like that tapping a card sent it
   wherever the game decided. Cards are dragged now, or picked up with a tap
   and put down with a second tap. This plays each of those for real: the
   mouse through Playwright's mouse, the finger through the browser's own
   touch events (CDP Input.dispatchTouchEvent), which the page receives as
   pointer events exactly as it would from a phone.

   Every case starts from a board laid out by hand, so the move it tries is
   known to be legal - or known not to be - and checks three things after:
   the cards are where the move says, nothing is left half-dragged (no ghost
   layer, no hidden card), and no page errors. */
const { chromium } = require('playwright');
const path = require('path');
process.chdir(path.join(__dirname, '..', '..'));
/* KL_URL=https://axesandaces.com/solitaire.html runs the same moves on the
   live site, which is how a publish is proved rather than assumed */
const URL = process.env.KL_URL || 'file:///' + path.resolve('solitaire.html').replace(/\\/g, '/');
const OUT = path.resolve('dev/gen/out/kldrag');
require('fs').mkdirSync(OUT, { recursive: true });

/* a board with one of everything worth testing:
     col 0  A of hearts, alone      -> goes home
     col 1  8 of spades             -> takes a red 7
     col 2  7 of hearts             -> goes onto col 1
     col 3  6 of clubs on 7 of diamonds, a run of two -> the pair onto col 4's 8 of clubs? no:
            the 7 of diamonds is red, so the pair goes onto a BLACK 8 - col 1 after it is used,
            so col 4 holds the 8 of clubs for it
     col 4  8 of clubs              -> takes the red 7 and the 6 riding on it
     col 5  K of spades, two buried -> nothing takes it but an empty column
     col 6  empty                   -> takes the king
   Suits: 0 spades, 1 hearts, 2 diamonds, 3 clubs. */
const LAYOUT = () => {
  const R = window.__SOL.R;
  const c = (r, s) => ({ r, s });
  R.cols = [
    { down:[], up:[c(1,1)] },
    { down:[c(2,0)], up:[c(8,0)] },
    { down:[c(3,0)], up:[c(7,1)] },
    { down:[c(4,0)], up:[c(7,2), c(6,3)] },
    { down:[c(5,0)], up:[c(8,3)] },
    { down:[c(9,0), c(10,0)], up:[c(13,0)] },
    { down:[], up:[] },
  ];
  R.found = [0,0,0,0]; R.done = []; R.waste = [c(12,2)]; R.stock = [c(2,2), c(3,3)];
  R.run = 0; R.runVal = 0; R.picked = null; R.wild = false; R.passes = 0;
  window.__SOL.render();
};

const state = p => p.evaluate(() => {
  const R = window.__SOL.R;
  const show = col => col.up.map(x => x.r + 'shdc'[x.s]).join(' ');
  return {
    cols: R.cols.map(show), found: R.found.slice(), run: R.run,
    ghost: !!document.getElementById('dragLayer'),
    hidden: [...document.querySelectorAll('.pk.kl')].filter(e => e.style.visibility === 'hidden').length,
    picked: R.picked ? `${R.picked.col}/${R.picked.n}` : null,
  };
});

/* centre of the TOP SLIVER of a card - what a thumb grabs on a covered card */
const grab = (p, sel) => p.evaluate(s => {
  const b = document.querySelector(s).getBoundingClientRect();
  return { x: b.left + b.width / 2, y: b.top + Math.min(8, b.height / 4) };
}, sel);
const middle = (p, sel) => p.evaluate(s => {
  const b = document.querySelector(s).getBoundingClientRect();
  return { x: b.left + b.width / 2, y: b.top + b.height / 2 };
}, sel);

async function mouseDrag(p, from, to, shot){
  await p.mouse.move(from.x, from.y);
  await p.mouse.down();
  /* in steps, the way a hand moves, so pointermove fires along the way */
  for(let i = 1; i <= 10; i++){
    await p.mouse.move(from.x + (to.x - from.x) * i / 10, from.y + (to.y - from.y) * i / 10);
    await p.waitForTimeout(12);
  }
  if(shot) await p.screenshot({ path: path.join(OUT, shot) });
  await p.mouse.up();
  await p.waitForTimeout(450);
}

async function touchDrag(cdp, p, from, to){
  const pt = (x, y) => [{ x: Math.round(x), y: Math.round(y), id: 1, radiusX: 8, radiusY: 8, force: 1 }];
  await cdp.send('Input.dispatchTouchEvent', { type:'touchStart', touchPoints: pt(from.x, from.y) });
  for(let i = 1; i <= 10; i++){
    await cdp.send('Input.dispatchTouchEvent', { type:'touchMove',
      touchPoints: pt(from.x + (to.x - from.x) * i / 10, from.y + (to.y - from.y) * i / 10) });
    await p.waitForTimeout(12);
  }
  await cdp.send('Input.dispatchTouchEvent', { type:'touchEnd', touchPoints: [] });
  await p.waitForTimeout(450);
}

(async () => {
  const b = await chromium.launch();
  let bad = 0;
  const check = (name, ok, s) => {
    const clean = !s.ghost && !s.hidden;
    if(!ok || !clean) bad++;
    console.log(`  ${(ok && clean) ? 'ok  ' : 'FAIL'} ${name.padEnd(42)} ` +
      (clean ? '' : `[left behind: ghost ${s.ghost}, hidden ${s.hidden}] `) +
      `cols ${JSON.stringify(s.cols)} home ${JSON.stringify(s.found)} held ${s.picked}`);
  };

  for(const [w, h, touch] of [[1280, 800, false], [390, 844, true]]){
    const ctx = await b.newContext({ viewport:{ width:w, height:h }, isMobile:touch, hasTouch:touch, deviceScaleFactor:2 });
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(String(e.message).slice(0, 140)));
    await p.route('**/*.{mp3,m4a,mp4,webm}', r => r.abort());
    await p.goto(URL, { waitUntil:'load' });
    await p.waitForTimeout(2000);
    for(let i = 0; i < 6; i++){
      if(!await p.evaluate(() => { const o = document.getElementById('overlay'); return o && !o.hidden; })) break;
      await p.click('#panel .btn.big[data-act], #panel [data-act]', { timeout: 2500 }).catch(() => {});
      await p.waitForTimeout(800);
    }
    await p.waitForFunction(() => !window.__SOL.busy, null, { timeout: 8000 }).catch(() => {});
    const cdp = touch ? await ctx.newCDPSession(p) : null;
    const move = (f, t, shot) => touch ? touchDrag(cdp, p, f, t) : mouseDrag(p, f, t, shot);
    console.log(`\n${w}x${h}, ${touch ? 'a finger' : 'a mouse'}`);

    /* 1. a card dragged home */
    await p.evaluate(LAYOUT);
    await move(await grab(p, '[data-col="0"][data-n="0"]'), await middle(p, '[data-home="1"]'), touch ? null : 'mid-drag.png');
    let s = await state(p);
    check('the ace dragged up to its home', s.found[1] === 1 && s.cols[0] === '' && s.run === 1, s);

    /* 2. a card dragged onto a column */
    await p.evaluate(LAYOUT);
    await move(await grab(p, '[data-col="2"][data-n="0"]'), await middle(p, '[data-col="1"][data-n="0"]'));
    s = await state(p);
    check('a red 7 dragged onto a black 8', s.cols[1] === '8s 7h' && s.cols[2] === '3s', s);

    /* 3. a run of two dragged by the card at its bottom */
    await p.evaluate(LAYOUT);
    await move(await grab(p, '[data-col="3"][data-n="0"]'), await middle(p, '[data-col="4"][data-n="0"]'));
    s = await state(p);
    check('a 7 and the 6 on it dragged together', s.cols[4] === '8c 7d 6c' && s.cols[3] === '4s', s);

    /* 4. a king into an empty column */
    await p.evaluate(LAYOUT);
    await move(await grab(p, '[data-col="5"][data-n="0"]'), await middle(p, '[data-empty-col="6"]'));
    s = await state(p);
    check('a king dragged into the empty column', s.cols[6] === '13s' && s.cols[5] === '10s', s);

    /* 5. an illegal drop goes back */
    await p.evaluate(LAYOUT);
    await move(await grab(p, '[data-col="1"][data-n="0"]'), await middle(p, '[data-col="4"][data-n="0"]'));
    s = await state(p);
    check('a black 8 on a black 8 goes back', s.cols[1] === '8s' && s.cols[4] === '8c', s);

    /* 6. dropped in empty space goes back */
    await p.evaluate(LAYOUT);
    const far = await middle(p, '#stage');
    await move(await grab(p, '[data-col="2"][data-n="0"]'), far);
    s = await state(p);
    check('dropped on the monster goes back', s.cols[2] === '7h' && s.cols[1] === '8s', s);

    /* 7. tap, then tap where it goes */
    await p.evaluate(LAYOUT);
    const tap = async sel => { const m = await middle(p, sel);
      if(touch) await p.touchscreen.tap(m.x, m.y); else await p.mouse.click(m.x, m.y);
      await p.waitForTimeout(350); };
    await tap('[data-col="2"][data-n="0"]');
    s = await state(p);
    check('a tap picks a card up and moves nothing', s.picked === '2/0' && s.cols[2] === '7h', s);
    await tap('[data-col="1"][data-n="0"]');
    s = await state(p);
    check('a second tap puts it down there', s.cols[1] === '8s 7h' && !s.picked, s);

    /* 8. a tap where it cannot go puts it back in the hand, not on the board */
    await p.evaluate(LAYOUT);
    await tap('[data-col="1"][data-n="0"]');
    await tap('[data-col="4"][data-n="0"]');
    s = await state(p);
    check('8 on 8 by tapping picks up the other 8', s.picked === '4/0' && s.cols[1] === '8s', s);
    await tap('[data-col="4"][data-n="0"]');
    s = await state(p);
    check('tapping the held card again drops it', !s.picked, s);

    /* 9. the deck still turns with a tap */
    await p.evaluate(LAYOUT);
    const before = await p.evaluate(() => window.__SOL.R.stock.length);
    await tap('[data-act="draw"]');
    const after = await p.evaluate(() => window.__SOL.R.stock.length);
    const s9 = await state(p);
    check('a tap on the deck turns a card', after === before - 1, s9);

    /* 10. what the game never does any more: send a card where IT chooses */
    await p.evaluate(LAYOUT);
    await tap('[data-col="0"][data-n="0"]');
    s = await state(p);
    check('tapping the ace does NOT send it home', s.found[1] === 0 && s.picked === '0/0', s);

    if(errs.length){ bad++; console.log('  page errors: ' + [...new Set(errs)].join(' | ')); }
    await p.evaluate(LAYOUT); await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(OUT, `felt-${w}.png`) });
    await ctx.close();
  }
  console.log(bad ? `\n${bad} problems` : '\nevery move goes where the player puts it, and nowhere else');
  console.log(`screenshots in ${OUT}`);
  await b.close();
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
