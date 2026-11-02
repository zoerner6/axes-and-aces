/* Does the music follow the world and the boss, and do the toggles stick?

   node dev/gen/slmusic.cjs

   The songs themselves are the card game's recordings and are not in
   question; what is in question is whether this game asks for the right one.
   So this checks the choice rather than the sound: every world, a boss, an
   ordinary fight, the merchant, the story - and then whether turning the
   music off survives a reload, which is the whole point of a toggle. */
const { chromium } = require('playwright');
const { openGame } = require('./slopen.cjs');
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..', '..');
execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const file = path.join(ROOT, 'solitaire.html').replace(/\\/g, '/');

const HAVE = new Set(fs.readdirSync(path.join(ROOT, 'music')).map(f => f.replace(/\.mp3$/, '')));

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  await p.route('**/vid/**', r => r.abort());
  await p.route('**/music/**', r => r.abort());   /* the choice is the question, not the sound */
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
  await p.goto('file://' + file, { waitUntil: 'load' });
  await p.waitForTimeout(400);
  await openGame(p);

  let bad = 0;
  const say = (what, got, want) => {
    const ok = got === want && (want === null || HAVE.has(want));
    if (!ok) bad++;
    console.log(`  ${what.padEnd(28)} asks for ${String(got).padEnd(8)} ` +
      `${ok ? '' : `*** expected ${want}${want && !HAVE.has(want) ? ', and there is no such file' : ''} ***`}`);
  };

  /* every world, out of a fight */
  for (let w = 0; w < 10; w++) {
    const got = await p.evaluate(wi => {
      const SOL = window.__SOL, S = SOL.S;
      S.world = wi; S.phase = 'camp';
      return SOL.songWant();
    }, w);
    say(`world ${w + 1}, at the merchant`, got, 'w' + (w + 1));
  }

  /* in a fight, ordinary and boss */
  const ordinary = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.world = 0; S.phase = 'fight'; S.step = 0; S.fight.boss = false;
    return SOL.songWant();
  });
  say('an ordinary fight', ordinary, 'fight1');
  const other = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.step = 1; return SOL.songWant();
  });
  say('the next ordinary fight', other, 'fight2');
  const boss = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.fight.boss = true; return SOL.songWant();
  });
  say('a boss', boss, 'boss');

  /* the eleventh world and beyond wrap round, so the Endless depths still
     have something to play */
  const endless = await p.evaluate(() => {
    const SOL = window.__SOL, S = SOL.S;
    S.world = 13; S.phase = 'camp'; S.fight.boss = false;
    return SOL.songWant();
  });
  say('Endless, depth 4', endless, 'w4');

  /* off means off */
  const off = await p.evaluate(() => {
    const SOL = window.__SOL;
    SOL.musicOn = false;
    return SOL.songWant();
  });
  say('with the music off', off, null);

  /* and it has to survive a reload */
  await p.evaluate(() => {
    document.querySelector('.tool[data-act="menu"]').click();
  });
  await p.waitForTimeout(200);
  const before = await p.evaluate(() => {
    const t = [...document.querySelectorAll('[data-act="togMusic"]')][0];
    const was = t.querySelector('.cost').textContent.trim();
    t.click();
    return was;
  });
  await p.waitForTimeout(200);
  const after = await p.evaluate(() =>
    document.querySelector('[data-act="togMusic"] .cost').textContent.trim());
  const stored = await p.evaluate(() => localStorage.getItem('sl_music'));
  await p.reload({ waitUntil: 'load' });
  await p.waitForTimeout(400);
  const kept = await p.evaluate(() => window.__SOL.musicOn);
  const ok = before !== after && String(kept) === stored;
  if (!ok) bad++;
  console.log(`  the toggle                   ${before} -> ${after}, saved as ${stored}, ` +
    `still ${kept} after a reload  ${ok ? '' : '*** DOES NOT STICK ***'}`);

  console.log(errs.length ? `\nERRORS: ${[...new Set(errs)].join(' | ')}` : '\nno page errors');
  await b.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
