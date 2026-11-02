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
const { DOORS, openGame } = require('./slopen.cjs');
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
    await p.route('**/music/**', r => r.abort());   /* not what this one is measuring */
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 160)));
  p.on('console', m => {
    if (m.type() !== 'error') return;
    const t = m.text();
    if (/ERR_FAILED|ERR_ABORTED|vid\//.test(t)) return;   /* the clips we blocked ourselves */
    errs.push(t.replace(/\s+/g, ' ').slice(0, 160));
  });
  /* An unhandled promise rejection is not an uncaught exception, so pageerror
     never sees it. Every sequence in this game is a promise. */
  await p.addInitScript(() => {
    addEventListener('unhandledrejection', e =>
      console.error('UNHANDLED REJECTION: ' + ((e.reason && e.reason.stack) || e.reason)));
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
      busy: window.__SOL.busy,
      panel: document.getElementById('overlay').hidden ? '' :
        [...document.querySelectorAll('#panel [data-act]')].map(e => e.dataset.act).join(','),
      cleared: window.__SOL.cleared(), anyLegal: window.__SOL.anyLegal(),
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

  /* Every fight now opens behind an intro panel, so a bot has to walk through
     the door like a person does. It is also the only thing standing between a
     stray click and a thirty-second Playwright timeout. */
  /* A fight is bracketed by panels now, not just opened by one: the intro,
     then victory, then a level-up with a perk to pick, or the fallen screen.
     Clicking the board while any of them is up is a thirty-second Playwright
     timeout, so the bot walks through whatever door is in front of it. */
  const walkPanels = async () => {
    const went = await openGame(p);
    if (went.some(x => x.startsWith('a panel') || x.startsWith('still behind')))
      console.log('      ** ' + went.join(' -> '));
  };
  const dismissIntro = walkPanels;

  let barMismatch = 0, runMismatch = 0, wedged = 0, fights = 0, strikes = 0;
  const tiers = {};
  let maxRun = 0, totalBoards = 0;
  await dismissIntro();
  let st = await read();
  let fightKey = st.foeName + st.lvl + st.step;
  let guard = 0;

  console.log(`playing ${FIGHTS} fights at ${W}x${H}\n`);
  console.log(`  fight 1: ${st.foeName} Lv ${st.lvl}${st.boss ? ' (boss)' : ''}  ` +
    `${st.foeMax} health`);

  while (fights < FIGHTS && guard < 4000) {
    guard++;
    await dismissIntro();

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
      /* A card can stop being legal between reading the board and tapping it,
         and a card that is not legal carries aria-disabled, which Playwright
         waits on for thirty seconds. Fail fast and read the board again. */
      try {
        await p.click(`.peaks .pk[data-i="${st.free[0]}"].free`, { timeout: 2500 });
      } catch { st = await read(); continue; }
      await p.waitForTimeout(330);
      /* a card can bring a peak down, which is a whole blow of its own, so
         the board is not ready again just because the card flew */
      await settle();
    } else if (st.stockLeft > 0) {
      const before = { hp: st.foeHp, run: st.run };
      /* A panel can open while this click is still retrying - the monster
         dies on the strike before it - and then the overlay intercepts and
         Playwright waits thirty seconds. Fail fast and look again. */
      try { await p.click('[data-act="turn"]', { timeout: 3000 }); }
      catch { await walkPanels(); st = await read(); continue; }
      if (before.run > 0) {
        /* a strike: catch the number it claims and check the health against it */
        let shown = null;
        try {
          await p.waitForSelector('.dmgnum', { timeout: 6000 });
          await p.waitForFunction(() => {
            const n = document.querySelector('.dmgnum');
            return n && n.classList.contains('out');
          }, null, { timeout: 8000 });
          /* Read the health in the SAME breath as the number. The monster's
             answer comes a beat later and a third of the pool heals itself,
             so comparing against the health after the answer reported the
             heal as the bar disagreeing with the game. */
          shown = await p.evaluate(() => {
            const n = document.querySelector('.dmgnum');
            return n ? { n: +n.textContent.replace(/[^0-9]/g, ''),
                         hp: window.__SOL.S.fight.hp } : null;
          });
        } catch { /* the monster may have died before the number settled */ }
        strikes++;
        const t = await p.evaluate(() => {
          const b = document.querySelector('#banner');
          return b ? (b.textContent || '').split(/Run of/)[0].trim() : '';
        });
        if (t) tiers[t] = (tiers[t] || 0) + 1;
        await settle();
        if (shown && Math.abs((before.hp - shown.hp) - shown.n) > 1) {
          barMismatch++;
          if (barMismatch < 5) console.log(`      ** said ${shown.n} damage, health fell ` +
            `${before.hp - shown.hp} (${before.hp} to ${shown.hp})`);
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
        /* A panel in front of the board is not a wedge - it is the game
           waiting for a player. Dying is the loud one: the fallen screen
           leaves the board behind it frozen on purpose, and three separate
           times that looked from out here like a board that would not move. */
        const st1 = await read();
        if (st1.panel) { await walkPanels(); st = await read(); continue; }
        wedged++;
        const st2 = await read();
        console.log(`      ** the board will not move and nothing redealt it ` +
          `(${st2.left} cards left, stock ${st2.stockLeft}, run ${st2.run}, ` +
          `busy ${st2.busy}, cleared ${st2.cleared}, anyLegal ${st2.anyLegal}, ` +
          `panel "${st2.panel}")`);
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
