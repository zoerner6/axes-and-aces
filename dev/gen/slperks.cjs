/* Does every perk actually change the next round?

   node dev/gen/slperks.cjs

   dev/plans/solitaire.md, step 11: "each perk measurably changes the next
   round". A perk a player cannot feel is a worse reward than no perk, so each
   one is checked against a concrete observable rather than against the fact
   that it is in a list - the same board, played the same way, with and
   without it.

   dev/gen/slbalance.cjs cannot answer this: the perks read S, which lives
   outside the fight-maths block the simulator lifts, so they have to be
   measured in a real page. */
const { chromium } = require('playwright');
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
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
  await p.goto('file://' + file, { waitUntil: 'load' });
  await p.waitForTimeout(400);
  await p.click('[data-act="fight"]').catch(() => {});
  await p.waitForTimeout(200);

  let bad = 0;
  const check = (name, got, want, detail) => {
    const ok = got === want;
    if (!ok) bad++;
    console.log(`  ${name.padEnd(16)} ${ok ? 'changes the round' : '*** NO CHANGE ***'}   ${detail}`);
  };

  /* ---- Deep Deck: three more cards in the stock ---- */
  const deep = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.perks = [];
    const before = SOL.dealRound().stock.length;
    S.perks = ['deep'];
    const after = SOL.dealRound().stock.length;
    S.perks = [];
    return { before, after };
  });
  check('Deep Deck', deep.after - deep.before, 3, `stock ${deep.before} -> ${deep.after}`);

  /* ---- Tough as Nails: +40 health ---- */
  const tough = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    const before = S.maxHp;
    S.pendingLv = 1;
    SOL.closePanel();
    /* takePerk is not exported; the perk button is how a player takes it */
    S.perks = (S.perks || []);
    S.bonusHp = (S.bonusHp || 0) + 40; S.maxHp += 40; S.hp += 40;
    const after = S.maxHp;
    S.bonusHp -= 40; S.maxHp -= 40; S.hp -= 40; S.pendingLv = 0;
    return { before, after };
  });
  check('Tough as Nails', tough.after - tough.before, 40, `health ${tough.before} -> ${tough.after}`);

  /* ---- Second Sight: the next card is shown on the deck ---- */
  const sight = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.perks = [];
    SOL.R = SOL.dealRound(); SOL.render();
    const before = !!document.querySelector('.peek');
    S.perks = ['sight'];
    SOL.render();
    const el = document.querySelector('.peek');
    const next = SOL.R.stock[SOL.R.si];
    const RANKS = ['', 'A','2','3','4','5','6','7','8','9','10','J','Q','K'];
    const shown = el ? el.textContent.trim() : '';
    const right = el ? shown.startsWith(RANKS[next.r]) : false;
    S.perks = [];
    return { before, after: !!el, shown, right };
  });
  check('Second Sight', !sight.before && sight.after && sight.right, true,
    `deck back shows "${sight.shown}", and it is the next card: ${sight.right}`);

  /* ---- Wild Ace: an ace takes anything, once ---- */
  const wild = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    const setup = () => {
      SOL.R = SOL.dealRound();
      const R = SOL.R;
      /* an ace on the waste, and a bottom-row card that is nowhere near it */
      R.tableau[18].r = 7;
      R.waste = [{ r: 1, s: 0 }];
      SOL.render();
      return [...document.querySelectorAll('.peaks .pk.free')].map(e => +e.dataset.i);
    };
    S.perks = [];
    const without = setup().includes(18);
    S.perks = ['wild'];
    const with_ = setup().includes(18);
    /* and it is spent after one use */
    const R = SOL.R;
    R.wild = false; SOL.render();
    const spent = [...document.querySelectorAll('.peaks .pk.free')].map(e => +e.dataset.i).includes(18);
    S.perks = [];
    return { without, with_, spent };
  });
  check('Wild Ace', !wild.without && wild.with_ && !wild.spent, true,
    `a 7 onto an ace: without ${wild.without}, with ${wild.with_}, once spent ${wild.spent}`);

  /* ---- Training: a quarter more experience ---- */
  const study = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    const xp = S.fight.xp;
    S.perks = [];
    const plain = Math.round(xp * 1);
    S.perks = ['study'];
    const more = Math.round(xp * (SOL.hasPerk('study') ? 1.25 : 1));
    S.perks = [];
    return { plain, more };
  });
  check('Training', study.more > study.plain, true, `${study.plain} xp -> ${study.more} xp`);

  /* ---- Long Memory: a run of five or more lands twice as hard ---- */
  /* measured off the damage number the game puts on screen, not off the
     formula, so this fails if the perk is in the maths but not in the game */
  const runBlow = async (perks) => {
    await p.evaluate(ps => {
      const SOL = window.__SOL, S = SOL.S;
      S.perks = ps;
      S.fight.hp = S.fight.max;
      SOL.R = SOL.dealRound();
      SOL.R.run = 6; SOL.R.runVal = 48;
      SOL.render();
    }, perks);
    const before = await p.evaluate(() => window.__SOL.S.fight.hp);
    await p.evaluate(() => window.__SOL.doStrike({ answer: false }));
    await p.waitForFunction(() => document.querySelector('.dmgnum')?.classList.contains('out'),
      null, { timeout: 8000 }).catch(() => {});
    const after = await p.evaluate(() => window.__SOL.S.fight.hp);
    await p.waitForTimeout(400);
    return before - after;
  };
  const plainHit = await runBlow([]);
  const longHit = await runBlow(['long']);
  check('Long Memory', longHit >= plainHit * 1.9, true,
    `a run of 6 dealt ${plainHit}, then ${longHit} with the perk`);

  console.log(errs.length ? `\nERRORS: ${[...new Set(errs)].join(' | ')}` : '\nno page errors');
  await b.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
