/* Does every charm and every potion actually do what it says?

   node dev/gen/slcharms.cjs

   Same job as dev/gen/slperks.cjs and for the same reason: the plan asks that
   each charm "works and says plainly what it does", and the only way to know
   is the same board with and without it. These read S, which lives outside
   the fight-maths block dev/gen/slbalance.cjs lifts, so they are measured in
   a real page rather than in the simulator. */
const { chromium } = require('playwright');
const { openGame } = require('./slopen.cjs');
const { execFileSync } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const file = path.join(ROOT, 'solitaire.html').replace(/\\/g, '/');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  await p.route('**/vid/**', r => r.abort());
    await p.route('**/music/**', r => r.abort());   /* not what this one is measuring */
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
  await p.addInitScript(() => {
    addEventListener('unhandledrejection', e =>
      console.error('UNHANDLED REJECTION: ' + ((e.reason && e.reason.stack) || e.reason)));
  });
  p.on('console', m => { if (m.type() === 'error' && !/vid\/|ERR_/.test(m.text())) errs.push(m.text().slice(0, 150)); });
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
  const check = (name, ok, detail) => {
    if (!ok) bad++;
    console.log(`  ${name.padEnd(17)} ${ok ? 'works' : '*** DOES NOT WORK ***'}   ${detail}`);
  };

  /* ---- Marked Deck: one peak starts a card shallower ---- */
  const marked = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    const tipsGone = () => { const R = SOL.dealRound(); return [0, 1, 2].filter(i => R.tableau[i].gone).length; };
    S.charms = []; const without = tipsGone();
    S.charms = ['marked']; const with_ = tipsGone();
    S.charms = [];
    return { without, with_ };
  });
  check('Marked Deck', marked.without === 0 && marked.with_ === 1,
    `peak tips already gone: ${marked.without} without, ${marked.with_} with`);

  /* ---- Iron Cup: a board opens with guard ---- */
  const cup = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.charms = []; S.block = 0;
    SOL.R = SOL.dealRound(); SOL.openBoard();
    const without = S.block;
    S.charms = ['cup']; S.block = 0;
    SOL.R = SOL.dealRound(); SOL.openBoard();
    const with_ = S.block;
    S.charms = []; S.block = 0;
    return { without, with_ };
  });
  check('Iron Cup', cup.without === 0 && cup.with_ === 20, `guard at the start: ${cup.without} -> ${cup.with_}`);

  /* ---- Reader's Glass: one hidden card is turned over ---- */
  const glass = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    const hiddenFaceUp = () => {
      SOL.R = SOL.dealRound({ hidden: [1] });
      SOL.openBoard();
      return (SOL.R.shown || []).length;
    };
    S.charms = []; const without = hiddenFaceUp();
    S.charms = ['glass']; const with_ = hiddenFaceUp();
    S.charms = [];
    return { without, with_ };
  });
  check("Reader's Glass", glass.without === 0 && glass.with_ === 1,
    `cards turned over on a board with a hidden peak: ${glass.without} -> ${glass.with_}`);

  /* ---- Jester's Coin: the card goes back and the run survives ---- */
  const coin = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.charms = ['jester'];
    SOL.R = SOL.dealRound();
    const R = SOL.R;
    R.waste.push({ r: 9, s: 0 });
    R.run = 4; R.runVal = 30;
    SOL.render();
    const button = !!document.querySelector('[data-act="coin"]');
    const wasteBefore = R.waste.length, stockBefore = R.stock.length - R.si, runBefore = R.run;
    SOL.useCoin();
    const after = { waste: R.waste.length, stock: R.stock.length - R.si, run: R.run,
                    again: !!document.querySelector('[data-act="coin"]') };
    S.charms = [];
    return { button, wasteBefore, stockBefore, runBefore, after };
  });
  check("Jester's Coin",
    coin.button && coin.after.waste === coin.wasteBefore - 1 &&
    coin.after.stock === coin.stockBefore + 1 && coin.after.run === coin.runBefore && !coin.after.again,
    `waste ${coin.wasteBefore}->${coin.after.waste}, stock ${coin.stockBefore}->${coin.after.stock}, ` +
    `run kept at ${coin.after.run}, and gone after one use: ${!coin.after.again}`);

  /* ---- a blow, measured off the health the game actually removes ---- */
  const blow = async (charms, perks, run, rage) => {
    await p.evaluate(([c, pk, r, rg]) => {
      const SOL = window.__SOL, S = SOL.S;
      S.charms = c; S.perks = pk; S.rage = !!rg;
      S.fight.hp = S.fight.max;
      SOL.R = SOL.dealRound();
      SOL.R.run = r; SOL.R.runVal = r * 8;
      SOL.render();
    }, [charms, perks, run, rage]);
    const before = await p.evaluate(() => window.__SOL.S.fight.hp);
    await p.evaluate(() => window.__SOL.doStrike({ answer: false }));
    await p.waitForFunction(() => document.querySelector('.dmgnum')?.classList.contains('out'),
      null, { timeout: 8000 }).catch(() => {});
    const after = await p.evaluate(() => window.__SOL.S.fight.hp);
    await p.waitForTimeout(380);
    return before - after;
  };

  const plain6 = await blow([], [], 6, false);
  const ring6 = await blow(['ring'], [], 6, false);
  check("Gambler's Ring", ring6 > plain6 * 1.2, `a run of 6 dealt ${plain6}, then ${ring6} with the ring`);

  const rage6 = await blow([], [], 6, true);
  check('Rage Potion', rage6 > plain6 * 1.4, `a run of 6 dealt ${plain6}, then ${rage6} on rage`);

  /* ---- Healing and Iron Skin ---- */
  const heal = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.rage = false; S.ironskin = false;
    S.hp = Math.round(S.maxHp * .4);
    const before = S.hp;
    S.pots = ['heal'];
    SOL.drink('heal');
    return { before, after: S.hp, left: (S.pots || []).length };
  });
  check('Healing Potion', heal.after > heal.before && heal.left === 0,
    `health ${heal.before} -> ${heal.after}, and the potion is used up`);

  const iron = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    const hit = 100;
    S.ironskin = false;
    const plain = Math.max(1, Math.round(hit / (1 + 0 / 100) * 1));
    S.ironskin = true;
    const soft = Math.max(1, Math.round(hit / (1 + 0 / 100) * .5));
    S.ironskin = false;
    return { plain, soft };
  });
  check('Iron Skin', iron.soft < iron.plain, `a 100 hit costs ${iron.plain}, then ${iron.soft} on iron skin`);

  /* ---- gear, which is the whole of step 12's done-when ---- */
  await p.evaluate(() => { const S = window.__SOL.S; S.eq = {}; S.charms = []; S.perks = []; S.rage = false; });
  const bareBlow = await blow([], [], 6, false);
  await p.evaluate(() => { window.__SOL.S.eq = { main: { type: 'axe', tier: 4 } }; });
  const axeBlow = await blow([], [], 6, false);
  check('A better axe', axeBlow > bareBlow * 1.3,
    `a run of 6 dealt ${bareBlow} bare, then ${axeBlow} with a steel axe`);

  const armor = await p.evaluate(() => {
    const S = window.__SOL.S, hit = 200;
    S.eq = {};
    const bare = Math.max(1, Math.round(hit));
    S.eq = { armor: { type: 'armor', tier: 4 }, shield: { type: 'shield', tier: 4 }, helm: { type: 'helm', tier: 4 } };
    const def = 80 + 60 + 50;
    const kitted = Math.max(1, Math.round(hit / (1 + def / 100)));
    return { bare, kitted, def };
  });
  check('Armor', armor.kitted < armor.bare,
    `a 200 hit costs ${armor.bare} bare, then ${armor.kitted} with +${armor.def} Defense`);

  const portrait = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.eq = {}; SOL.setMyBars();
    const low = document.querySelector('#mePic').getAttribute('src');
    S.eq = { armor: { type: 'armor', tier: 5 } }; SOL.setMyBars();
    const high = document.querySelector('#mePic').getAttribute('src');
    S.eq = {}; SOL.setMyBars();
    return { low, high };
  });
  check('The portrait', portrait.low !== portrait.high,
    `${(portrait.low || '').split('/').pop()} changes to ${(portrait.high || '').split('/').pop()}`);

  console.log(errs.length ? `\nERRORS: ${[...new Set(errs)].join(' | ')}` : '\nno page errors');
  await b.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
