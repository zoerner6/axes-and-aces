/* Play real Monster Solitaire fights in a browser, the way a person would.

   node dev/gen/slplay.cjs [fights] [--size 390x844]

   dev/gen/slbalance.cjs answers whether the numbers are fair. This answers
   whether the game actually does what the numbers say: that the health bar
   moves by exactly what the damage number claimed, that a long run reads as a
   bigger event than a short one, that the loop never wedges, and that nothing
   throws.

   It reads the game's own state through window.__SOL rather than the screen,
   and the screen through the health bar, so a disagreement between the two is
   the thing it is looking for. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const args = process.argv.slice(2);
const FIGHTS = +(args[0] || 3) || 3;
const sizeArg = args.includes('--size') ? args[args.indexOf('--size') + 1] : '390x844';
const [W, H] = sizeArg.split('x').map(Number);

execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const file = path.join(ROOT, 'solitaire.html').replace(/\\/g, '/');

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1,
    isMobile: W <= 560, hasTouch: W <= 560, reducedMotion: 'no-preference' });
  const p = await ctx.newPage();
  await p.route('**/vid/**', r => r.abort());      /* 585MB, and not what is being checked */
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 160)));
  p.on('console', m => {
    if (m.type() !== 'error') return;
    const t = m.text();
    if (/ERR_FAILED|ERR_ABORTED|vid\//.test(t)) return;   /* the clips we blocked ourselves */
    errs.push(t.replace(/\s+/g, ' ').slice(0, 160));
  });
  await p.goto('file://' + file, { waitUntil: 'load' });
  await p.waitForTimeout(500);

  const read = () => p.evaluate(() => {
    const S = window.__SOL.S, R = window.__SOL.R, f = S.fight;
    const bar = document.querySelector('#foeBar');
    const mine = document.querySelector('#myBar');
    return {
      foeHp: f ? f.hp : 0, foeMax: f ? f.max : 1, foeName: f ? f.name : '',
      boss: !!(f && f.boss), lvl: f ? f.lvl : 0,
      hp: S.hp, maxHp: S.maxHp, level: S.level, step: S.step, gold: S.gold,
      run: R.run, stockLeft: R.stock.length - R.si,
      free: [...document.querySelectorAll('.peaks .pk.free')].map(e => +e.dataset.i),
      left: document.querySelectorAll('.peaks .pk').length,
      barPc: parseFloat(bar.style.height) || 0,
      myPc: parseFloat(mine.style.width) || 0,
      shownRun: +(document.querySelector('#runbox b') || {}).textContent,
      busyish: !!document.querySelector('.dmgnum, .boom, .slash'),
    };
  });

  /* wait until the strike sequence has finished and the board responds again */
  const settle = async () => {
    try {
      await p.waitForFunction(() => !document.querySelector('.dmgnum, .boom, .slash, .claw'),
        null, { timeout: 15000 });
    } catch { /* fall through and let the caller notice nothing moved */ }
    await p.waitForTimeout(140);
  };

  let barMismatch = 0, runMismatch = 0, wedged = 0, fights = 0, strikes = 0;
  const tiers = {};
  let maxRun = 0, totalBoards = 0;
  let st = await read();
  let fightKey = st.foeName + st.lvl + st.step;
  let guard = 0;

  console.log(`playing ${FIGHTS} fights at ${W}x${H}\n`);
  console.log(`  fight 1: ${st.foeName} Lv ${st.lvl}${st.boss ? ' (boss)' : ''}  ` +
    `${st.foeMax} health`);

  while (fights < FIGHTS && guard < 4000) {
    guard++;

    /* the bar on screen has to agree with the health in the game */
    const want = Math.max(0, st.foeHp / st.foeMax * 100);
    if (Math.abs(want - st.barPc) > 0.6) {
      barMismatch++;
      if (barMismatch < 4) console.log(`      ** health bar says ${st.barPc.toFixed(1)}% ` +
        `but the monster is on ${want.toFixed(1)}% (${st.foeHp} of ${st.foeMax})`);
    }
    if (st.shownRun !== st.run) {
      runMismatch++;
      if (runMismatch < 4) console.log(`      ** run counter shows ${st.shownRun}, the game has ${st.run}`);
    }
    if (st.run > maxRun) maxRun = st.run;

    if (st.free.length) {
      await p.click(`.peaks .pk[data-i="${st.free[0]}"]`);
      await p.waitForTimeout(330);
    } else if (st.stockLeft > 0) {
      const before = { hp: st.foeHp, run: st.run };
      await p.click('[data-act="turn"]');
      if (before.run > 0) {
        /* a strike: catch the number it claims and check the health against it */
        let shown = null;
        try {
          await p.waitForSelector('.dmgnum', { timeout: 6000 });
          await p.waitForFunction(() => {
            const n = document.querySelector('.dmgnum');
            return n && n.classList.contains('out');
          }, null, { timeout: 8000 });
          shown = await p.evaluate(() => {
            const n = document.querySelector('.dmgnum');
            return n ? +n.textContent.replace(/[^0-9]/g, '') : null;
          });
        } catch { /* the monster may have died before the number settled */ }
        strikes++;
        const t = await p.evaluate(() => {
          const b = document.querySelector('#banner');
          return b ? (b.textContent || '').split(/Run of/)[0].trim() : '';
        });
        if (t) tiers[t] = (tiers[t] || 0) + 1;
        await settle();
        const after = await read();
        /* the monster may have healed or guarded straight after, so this only
           checks the drop was at least what the number said */
        if (shown != null && after.foeHp > 0 && before.hp - after.foeHp < shown - 1) {
          barMismatch++;
          if (barMismatch < 5) console.log(`      ** said ${shown} damage, health fell ` +
            `${before.hp - after.foeHp} (${before.hp} to ${after.foeHp})`);
        }
      } else {
        await p.waitForTimeout(200);
      }
      await settle();
    } else {
      /* No legal card and no stock, so the game has to redeal itself - but
         first it lands the run and takes a free swing, and the swing waits on
         the monster's own attack clip, which for a Bandit Chief lands at 2.2
         seconds. Waiting a flat moment here called that a wedge. */
      const was = { left: st.left, stock: st.stockLeft, name: st.foeName + st.step };
      let moved = false;
      try {
        await p.waitForFunction(w => {
          const R = window.__SOL.R, S = window.__SOL.S;
          return R.stock.length - R.si > 0 ||
                 document.querySelectorAll('.peaks .pk').length !== w.left ||
                 (S.fight.name + S.step) !== w.name;
        }, was, { timeout: 20000 });
        moved = true;
      } catch { /* reported below */ }
      await settle();
      if (!moved) {
        wedged++;
        const st2 = await read();
        console.log(`      ** the board will not move and nothing redealt it ` +
          `(${st2.left} cards left, stock ${st2.stockLeft}, run ${st2.run})`);
        break;
      }
      totalBoards++;
    }

    st = await read();
    const key = st.foeName + st.lvl + st.step;
    if (key !== fightKey) {
      fights++;
      fightKey = key;
      if (fights < FIGHTS) console.log(`  fight ${fights + 1}: ${st.foeName} Lv ${st.lvl}` +
        `${st.boss ? ' (boss)' : ''}  ${st.foeMax} health   ` +
        `(you: ${st.hp}/${st.maxHp}, ${st.gold} gold)`);
    }
  }

  console.log(`\n${fights} fights, ${strikes} strikes, longest run ${maxRun}`);
  console.log('tiers seen: ' + (Object.keys(tiers).length
    ? Object.entries(tiers).map(([k, v]) => `${k} ${v}`).join(', ') : 'none'));
  console.log(`health bar disagreed ${barMismatch} times, run counter ${runMismatch}, wedged ${wedged}`);
  console.log(errs.length ? `CONSOLE ERRORS:\n  ${[...new Set(errs)].join('\n  ')}` : 'no console errors');

  await b.close();
  if (barMismatch || runMismatch || wedged || errs.length || fights === 0) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
