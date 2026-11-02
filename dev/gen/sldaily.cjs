/* Do two people playing today's challenge get the same game?

   node dev/gen/sldaily.cjs

   dev/plans/solitaire.md, step 22: "two fresh browsers on the same day get
   identical deals". So this opens two, with separate storage, and compares
   what each is actually given - the monster, its health, the twenty-eight
   cards on the table and the order of the stock behind them - across all five
   fights. Comparing only the cards would miss two players fighting different
   monsters with the same deal, which is the mistake that is easy to make when
   only the shuffle is seeded.

   It also checks the opposite: that an ordinary game is NOT the same twice,
   because a seed left switched on would be a far quieter bug than one left
   off. */
const { chromium } = require('playwright');
const { openGame } = require('./slopen.cjs');
const { execFileSync } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const file = 'file://' + path.join(ROOT, 'solitaire.html').replace(/\\/g, '/');

/* everything a player is handed at the start of a fight */
const SNAPSHOT = () => {
  const SOL = window.__SOL, S = SOL.S, R = SOL.R;
  const card = c => `${c.r}${'shdc'[c.s]}`;
  return {
    foe: S.fight ? `${S.fight.slug} lv${S.fight.lvl} ${S.fight.hp}hp${S.fight.boss ? ' boss' : ''}` : '-',
    table: R.tableau.map(card).join(','),
    stock: R.stock.map(card).join(','),
    n: S.daily ? S.daily.n : -1
  };
};

async function runDaily(browser, fights) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  await p.route('**/vid/**', r => r.abort());
  await p.route('**/music/**', r => r.abort());
  await p.route(/\.netlify\/functions\//   /* a glob stops at the ?, and these all carry a query */, r =>
    r.fulfill({ status: 200, contentType: 'application/json', body: '{"scores":[]}' }));
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
  await p.goto(file, { waitUntil: 'load' });
  await p.waitForTimeout(400);
  await openGame(p);

  const shots = [];
  await p.evaluate(() => window.__SOL.startDaily());
  await p.waitForTimeout(200);
  await p.click('[data-act="dailyGo"]', { timeout: 4000 }).catch(() => {});
  await p.waitForTimeout(400);
  await openGame(p);
  shots.push(await p.evaluate(SNAPSHOT));

  /* walk the daily forward without playing it out: what is being compared is
     what each player is HANDED, not how well either of them plays */
  for (let i = 1; i < fights; i++) {
    await p.evaluate(() => window.__SOL.dailyNext());
    await p.waitForTimeout(250);
    await openGame(p);
    shots.push(await p.evaluate(SNAPSHOT));
  }
  const errOut = [...new Set(errs)];
  await ctx.close();
  return { shots, errs: errOut };
}

async function runOrdinary(browser) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  await p.route('**/vid/**', r => r.abort());
  await p.route('**/music/**', r => r.abort());
  await p.goto(file, { waitUntil: 'load' });
  await p.waitForTimeout(400);
  await openGame(p);
  const shot = await p.evaluate(SNAPSHOT);
  await ctx.close();
  return shot;
}

(async () => {
  const b = await chromium.launch();
  let bad = 0;

  const a = await runDaily(b, 5);
  const c = await runDaily(b, 5);

  for (let i = 0; i < a.shots.length; i++) {
    const x = a.shots[i], y = c.shots[i];
    const same = x.foe === y.foe && x.table === y.table && x.stock === y.stock;
    if (!same) bad++;
    console.log(`  fight ${i + 1}  ${same ? 'identical' : '*** DIFFERENT ***'}  ${x.foe}`);
    if (!same) {
      if (x.foe !== y.foe) console.log(`      monster: ${x.foe}  vs  ${y.foe}`);
      if (x.table !== y.table) console.log(`      table:   ${x.table.slice(0, 48)}...  vs  ${y.table.slice(0, 48)}...`);
      if (x.stock !== y.stock) console.log(`      stock:   ${x.stock.slice(0, 48)}...  vs  ${y.stock.slice(0, 48)}...`);
    }
  }

  const o1 = await runOrdinary(b), o2 = await runOrdinary(b);
  const differs = o1.table !== o2.table;
  if (!differs) bad++;
  console.log(`\n  an ordinary game  ${differs ? 'differs every time, as it should' : '*** IS THE SAME TWICE - a seed was left on ***'}`);

  const errs = [...new Set([...a.errs, ...c.errs])];
  console.log(errs.length ? `ERRORS: ${errs.join(' | ')}` : 'no page errors');
  await b.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
