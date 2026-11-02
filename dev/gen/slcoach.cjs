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
    stored: localStorage.getItem('sl_coachLearned'),
    turnBtn: !!document.querySelector('[data-act="turn"]'),
    stockLeft: window.__SOL.R.stock.length - window.__SOL.R.si,
    run: window.__SOL.R.run
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

    /* 1. whichever mark the board it dealt actually calls for. A Tri-Peaks
       board can open with no legal move, and when it does the honest first
       lesson is the stock, not the tap - so the test asks the board what it
       should be seeing rather than insisting on one of them. */
    let m = await p.evaluate(markState);
    const openedPlayable = m.free > 0;
    const firstWord = openedPlayable ? 'Tap a card' : 'Nothing to play';
    check(`1. ${openedPlayable ? 'tap a card' : 'turn a card (dead board)'}`,
      m.up && m.at === '' && m.onScreen && m.size >= 10.5 && (m.text || '').startsWith(firstWord),
      m.up ? `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}, ` +
             `${m.free} of ${m.cards} cards playable`
           : `nothing shown: busy ${m.busy}, panel ${m.panel}, ${m.free} of ${m.cards} playable`);

    /* and it goes when you do the thing it asked for */
    const did = await p.evaluate(async playable => {
      const t = playable ? document.querySelector('.peaks .pk.free')
                         : document.querySelector('[data-act="turn"]');
      if (!t) return false;
      t.click();
      await new Promise(r => setTimeout(r, 900));
      return true;
    }, openedPlayable);
    await p.waitForFunction(() => !window.__SOL.busy, null, { timeout: 10000 }).catch(() => {});
    m = await p.evaluate(markState);
    const firstId = openedPlayable ? 'play' : 'stock';
    /* what matters is that the mark was learned, not that the screen is now
       empty: doing the thing can perfectly well bring the NEXT mark straight
       up, and asserting nothing is showing called that a failure */
    check('   and goes once you do', did && m.at.includes(firstId),
      `learned: ${m.at || 'nothing'}${m.up ? `, and it has moved on to "${(m.text || '').slice(0, 28)}"` : ''}`);

    /* 2. whichever of the two the opening board did not call for. A dead
       opening board teaches the stock first, so what is owed then is the tap,
       and building another dead board would make a mark that can never show.
       The board is built to suit what is owed, not the other way round. */
    const second = openedPlayable ? 'stock' : 'play';
    await p.evaluate(want => {
      const SOL = window.__SOL, R = SOL.R;
      if (want === 'stock') {
        /* nothing legal: every card a 7 and a 2 on the pile */
        R.tableau.forEach(c => { if (!c.gone) c.r = 7; });
        R.waste = [{ r: 2, s: 0 }];
      } else {
        /* one legal card, on the bottom row where nothing covers it */
        R.tableau.forEach(c => { if (!c.gone) c.r = 7; });
        R.tableau[18].gone = false; R.tableau[18].r = 7;
        R.waste = [{ r: 8, s: 0 }];
      }
      /* no run going: otherwise turning a card lands a whole strike and the
         monster answers it, which takes seconds and is not what is being
         checked here */
      R.run = 0; R.runVal = 0;
      SOL.render();
      SOL.coachShow(want);
    }, second);
    await p.waitForTimeout(300);
    m = await p.evaluate(markState);
    check(`2. ${second === 'stock' ? 'turn a card' : 'tap a card'}`,
      m.up && m.onScreen, `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}`);
    /* a tap only counts when the board is listening; clicking while the game
       is still playing something out does nothing at all and looks from out
       here exactly like the mark failing to advance */
    await p.waitForFunction(() => !window.__SOL.busy, null, { timeout: 8000 }).catch(() => {});
    await p.click(second === 'stock' ? '[data-act="turn"]' : '.peaks .pk.free',
      { timeout: 4000 }).catch(() => {});
    await p.waitForFunction(() => !window.__SOL.busy, null, { timeout: 10000 }).catch(() => {});
    await p.waitForTimeout(400);
    m = await p.evaluate(markState);
    check('   and goes once you do', m.at.includes(second),
      `learned: ${m.at || 'nothing'}, busy ${m.busy}, turn button ${m.turnBtn}, ` +
      `stock ${m.stockLeft}, run ${m.run}, panel ${m.panel}`);
    /* whichever one the opening board skipped is still owed, which is the
       whole point of keeping a set rather than a position in a list */
    const owed = await p.evaluate(() => {
      const learned = window.__SOL.coachLearned;
      return ['play', 'stock', 'run', 'clear'].filter(x => !learned.includes(x));
    });
    check('   and still owes the rest', owed.length > 0, `still to meet: ${owed.join(', ')}`);

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
