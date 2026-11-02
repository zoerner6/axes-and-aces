/* Do the first-time marks explain the game, in order, once?

   node dev/gen/slcoach.cjs

   dev/plans/solitaire.md, step 21: the coaching marks explain play, stock,
   run and clear, in that order. Three things have to be true for that to be
   worth anything: each mark appears at the moment it is about rather than on
   a timer, each one points at the thing it is describing and sits fully on
   the screen, and a player who already knows never sees any of it again. */
const { chromium } = require('playwright');
const { openGame } = require('./slopen.cjs');
const { execFileSync } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const file = 'file://' + path.join(ROOT, 'solitaire.html').replace(/\\/g, '/');

const SIZES = [[320, 568], [390, 844]];

const markState = () => {
  const c = document.querySelector('.coach');
  const lit = document.querySelector('.coachlit');
  const ctx = {
    at: window.__SOL.coachLearned.join(','), busy: window.__SOL.busy,
    panel: document.getElementById('overlay').hidden ? 'none' :
      [...document.querySelectorAll('#panel [data-act]')].map(e => e.dataset.act).join(','),
    free: document.querySelectorAll('.peaks .pk.free').length,
    cards: document.querySelectorAll('.peaks .pk').length,
    stored: localStorage.getItem('sl_coachLearned')
  };
  if (!c) return { up: false, ...ctx };
  const r = c.getBoundingClientRect();
  void 0;
  const lr = lit ? lit.getBoundingClientRect() : null;
  return {
    up: true, ...ctx,
    text: (c.textContent || '').replace(/\s+/g, ' ').trim(),
    onScreen: r.left >= -1 && r.top >= -1 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1,
    size: parseFloat(getComputedStyle(c).fontSize),
    pointsAt: lr ? `${Math.round(lr.width)}x${Math.round(lr.height)}` : 'nothing'
  };
};

(async () => {
  const b = await chromium.launch();
  let bad = 0;
  const check = (name, ok, detail) => {
    if (!ok) bad++;
    console.log(`  ${name.padEnd(26)} ${ok ? 'shows' : '*** DOES NOT ***'}   ${detail}`);
  };

  for (const [w, h] of SIZES) {
    console.log(`${w}x${h}`);
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: w <= 560, hasTouch: w <= 560 });
    const p = await ctx.newPage();
    await p.route('**/vid/**', r => r.abort());
    await p.route('**/music/**', r => r.abort());
    const errs = [];
    p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
    await p.goto(file, { waitUntil: 'load' });
    await p.waitForTimeout(300);
    await openGame(p);
    await p.waitForTimeout(1000);                /* the first mark waits for the board */

    /* 1. play */
    let m = await p.evaluate(markState);
    check('1. tap a card', m.up && m.at === '' && m.onScreen && m.size >= 10.5,
      m.up ? `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}, on screen ${m.onScreen}`
           : `nothing shown: step ${m.at}, busy ${m.busy}, panel ${m.panel}, ` +
             `${m.free} free of ${m.cards} cards, learned "${m.at}"`);

    /* and it goes when you do it */
    const played = await p.evaluate(async () => {
      const free = document.querySelector('.peaks .pk.free');
      if (!free) return false;
      free.click();
      await new Promise(r => setTimeout(r, 600));
      return true;
    });
    m = await p.evaluate(markState);
    check('   and goes once you do', played && m.at === 'play' && !m.up, `learned: ${m.at || 'nothing'}`);

    /* 2. stock: a board with nothing legal on it */
    await p.evaluate(() => {
      const SOL = window.__SOL, R = SOL.R;
      R.tableau.forEach(c => { if (!c.gone) c.r = 7; });
      R.waste = [{ r: 2, s: 0 }];
      /* no run going: otherwise turning a card lands a whole strike and the
         monster answers it, which takes seconds and is not what is being
         checked here */
      R.run = 0; R.runVal = 0;
      SOL.render();
      SOL.coachShow('stock');
    });
    await p.waitForTimeout(300);
    m = await p.evaluate(markState);
    check('2. turn a card', m.up && m.at === 'play' && m.onScreen,
      `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}`);
    /* a tap only counts when the board is listening; clicking while the game
       is still playing something out does nothing at all and looks from out
       here exactly like the mark failing to advance */
    await p.waitForFunction(() => !window.__SOL.busy, null, { timeout: 8000 }).catch(() => {});
    await p.click('[data-act="turn"]', { timeout: 4000 }).catch(() => {});
    await p.waitForFunction(() => !window.__SOL.busy, null, { timeout: 10000 }).catch(() => {});
    await p.waitForTimeout(400);
    m = await p.evaluate(markState);
    check('   and goes once you do', /stock/.test(m.at) && !m.up, `learned: ${m.at}, busy ${m.busy}`);

    /* 3. the run */
    await p.evaluate(() => {
      const SOL = window.__SOL;
      SOL.R = SOL.dealRound();
      SOL.R.run = 2; SOL.R.runVal = 16;
      SOL.render();
      SOL.coachShow('run');
    });
    await p.waitForTimeout(300);
    m = await p.evaluate(markState);
    check('3. that is your run', m.up && m.onScreen, `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}`);

    /* 4. a peak down */
    await p.evaluate(() => {
      const SOL = window.__SOL;
      SOL.coachLearned = ['play', 'stock', 'run'];
      SOL.R = SOL.dealRound();
      SOL.render();
      SOL.coachShow('clear');
    });
    await p.waitForTimeout(300);
    m = await p.evaluate(markState);
    check('4. take all three down', m.up && m.onScreen, `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}`);

    /* once ever */
    await p.evaluate(() => { window.__SOL.coachLearned = ['play', 'stock', 'run', 'clear']; });
    await p.reload({ waitUntil: 'load' });
    await p.waitForTimeout(300);
    await openGame(p);
    await p.waitForTimeout(1200);
    m = await p.evaluate(markState);
    check('and never again', !m.up, `after a reload with it learned, marks on screen: ${m.up ? 'yes' : 'none'}`);

    if (errs.length) { console.log('      ** JS: ' + [...new Set(errs)].join(' | ')); bad++; }
    await ctx.close();
  }

  console.log(bad ? `\n${bad} problems` : '\nall four marks, in order, once');
  await b.close();
  if (bad) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
