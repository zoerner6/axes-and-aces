/* Do the first-time marks explain the game, in order, once?

   node dev/gen/slcoach.cjs

   dev/plans/solitaire.md, step 21: the coaching marks explain play, stock,
   run and clear, in that order. Three things have to be true for that to be
   worth anything: each mark appears at the moment it is about rather than on
   a timer, each one points at the thing it is describing and sits fully on
   the screen, and a player who already knows never sees any of it again. */
const { chromium } = require('playwright');

/* Which button ends a mark, on whichever board is on screen. This file was
   written against Tri-Peaks and clicked `.peaks .pk.free` and
   `[data-act="turn"]` outright, so on Klondike it clicked nothing and then
   reported the mark as failing to advance - a tool blaming the game for its
   own selector. */
/* Play one card the way a player now has to: on Klondike a card is DRAGGED
   to where it goes, because a click only picks it up. This used to click a
   lit card and let the game choose where it went; the game no longer
   chooses, so the tool carries it. Tri-Peaks still plays a card by clicking
   it, so that board keeps its click. */
async function playOne(p){
  const plan = await p.evaluate(() => {
    if (document.querySelector('.peaks')) {
      const t = document.querySelector('.peaks .pk.free');
      if (t) t.click();
      return t ? { clicked: true } : null;
    }
    const X = window.__SOL, R = X.R;
    const lit = document.querySelector('.pk.kl.live, [data-from="w"].live');
    if (!lit) return null;
    const from = lit.dataset.from === 'w'
      ? { col: -1, n: -1, card: R.waste[R.waste.length - 1] }
      : { col: +lit.dataset.col, n: +lit.dataset.n, card: R.cols[+lit.dataset.col].up[+lit.dataset.n] };
    const m = X.bestMove(from);
    if (!m) return null;
    const dest = m.to === 'found'
      ? document.querySelector(`[data-home="${from.card.s}"]`)
      : (document.querySelector(`.kl-col[data-col="${m.j}"] .pk:last-child`) ||
         document.querySelector(`.kl-col[data-col="${m.j}"]`));
    const a = lit.getBoundingClientRect(), b = dest.getBoundingClientRect();
    return { x0: a.left + a.width / 2, y0: a.top + Math.min(8, a.height / 4),
             x1: b.left + b.width / 2, y1: b.top + b.height / 2 };
  });
  if (!plan) return false;
  if (plan.clicked) { await p.waitForTimeout(900); return true; }
  await p.mouse.move(plan.x0, plan.y0);
  await p.mouse.down();
  for (let i = 1; i <= 10; i++) {
    await p.mouse.move(plan.x0 + (plan.x1 - plan.x0) * i / 10, plan.y0 + (plan.y1 - plan.y0) * i / 10);
    await p.waitForTimeout(12);
  }
  await p.mouse.up();
  await p.waitForTimeout(900);
  return true;
}

const boardSel = async (p, want) => p.evaluate(w => {
  const peaks = !!document.querySelector('.peaks');
  if (w === 'stock') return peaks ? '[data-act="turn"]' : '[data-act="draw"]';
  return peaks ? '.peaks .pk.free' : '.pk.kl.live, [data-from="w"].live';
}, want);
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
    free: document.querySelectorAll('.peaks .pk.free, .pk.kl.live, [data-from="w"].live').length,
    cards: document.querySelectorAll('.peaks .pk, .kl-col > .pk').length,
    stored: localStorage.getItem('sl_coachLearned'),
    turnBtn: !!document.querySelector('[data-act="turn"], [data-act="draw"]'),
    /* the two boards count their stock the opposite way: Tri-Peaks walks an
       index forward through it, Klondike pops off the end */
    stockLeft: window.__SOL.R.tableau
      ? window.__SOL.R.stock.length - window.__SOL.R.si
      : window.__SOL.R.stock.length,
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
    /* The words each mark opens with, from the board on screen. This said
       'Nothing to play' for a dead board, which is no longer anywhere in the
       game - the stock mark says 'Stuck?' on both boards - so a dead opening
       board failed this every time, and it only ever passed because most
       deals have something to play. Klondike's play mark says 'Drag' now
       that a click only picks a card up. */
    const onPeaks = await p.evaluate(() => !!document.querySelector('.peaks'));
    const firstWord = !openedPlayable ? 'Stuck?' : onPeaks ? 'Tap a card' : 'Drag a card';
    check(`1. ${openedPlayable ? 'move a card' : 'turn a card (dead board)'}`,
      m.up && m.at === '' && m.onScreen && m.size >= 10.5 && (m.text || '').startsWith(firstWord),
      m.up ? `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}, ` +
             `${m.free} of ${m.cards} cards playable`
           : `nothing shown: busy ${m.busy}, panel ${m.panel}, ${m.free} of ${m.cards} playable`);

    /* and it goes when you do the thing it asked for */
    /* "turn" on Tri-Peaks, "draw" on Klondike. This said "turn" outright,
       so on a dead Klondike opening board it clicked nothing and then
       reported the mark as never being learned - the tool blaming the game
       for its own selector, which is the same fault twice in one file. */
    const did = openedPlayable ? await playOne(p) : await p.evaluate(async () => {
      const t = document.querySelector('[data-act="turn"], [data-act="draw"]');
      if (!t) return false;
      t.click();
      await new Promise(r => setTimeout(r, 900));
      return true;
    });
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
      if (R.tableau) {
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
      } else {
        /* Klondike. Every column a lone black seven: a seven cannot sit on
           another seven and with no ace home none of them can go home, so
           the board is dead and the only thing left is the deck. */
        R.cols.forEach(col => { col.down = []; col.up = [{ r: 7, s: 0 }]; });
        R.found = [0, 0, 0, 0];
        R.waste = [];
        if (!R.stock.length) R.stock = [{ r: 9, s: 1 }, { r: 4, s: 3 }];
        R.passes = 0;
        /* and for the tap, exactly one card that can go home */
        if (want !== 'stock') R.cols[0].up = [{ r: 1, s: 0 }];
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
    if (second === 'stock') await p.click(await boardSel(p, second), { timeout: 4000 }).catch(() => {});
    else await playOne(p);
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
    check('4. a suit, or a peak, comes down', m.up && m.onScreen, `"${(m.text || '').slice(0, 44)}" pointing at ${m.pointsAt}`);

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
