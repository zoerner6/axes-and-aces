/* Does a new panel really cancel the one before it, on the live site?
     node dev/gen/fktimers.cjs

   clearPanelTimers() was defined in dev/farkle.html and never called. The
   check that passed it had looked for the function; the call was not there,
   so the bug stayed live. This one runs the thing instead: it starts a fight
   intro, which schedules its typing, replaces the panel underneath it, waits
   past both of those timers, and looks at what is on screen.

   If the cancel is wired in, the replacement panel still says what it said.
   If it is not, the old intro's line and caption type themselves into it. */
const { chromium } = require('playwright');

const SITE = process.argv[2] || 'https://axesandaces.com/farkle.html';

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(SITE, { waitUntil: 'load' });
  await p.waitForTimeout(2500);

  if (!await p.evaluate(() => !!window.__FK)) {
    console.log('FAIL  the page did not boot far enough to test'); process.exit(1);
  }

  const r = await p.evaluate(async () => {
    const FK = window.__FK;
    /* a fight intro schedules its line at ~700ms and its caption at ~1100ms */
    FK.S.introBeat = 9; FK.S.endBeat = 9;
    FK.startFight();
    await new Promise(z => setTimeout(z, 120));
    FK.openPanel('<p id="encSay">KEEP</p><p id="encCap">KEEP</p>');
    await new Promise(z => setTimeout(z, 1900));
    const g = id => (document.getElementById(id) || {}).textContent;
    return { say: g('encSay'), cap: g('encCap') };
  });

  const clean = r.say === 'KEEP' && r.cap === 'KEEP';
  console.log(`${clean ? '  ok  ' : 'FAIL  '}a new panel cancels the one before it`);
  console.log(`        the line reads    ${JSON.stringify(r.say)}`);
  console.log(`        the caption reads ${JSON.stringify(r.cap)}`);
  if (!clean) console.log('        a stale timer wrote into the panel that replaced it');
  console.log(`${errs.length ? 'FAIL  ' : '  ok  '}no script errors  ${errs.slice(0, 2).join(' | ')}`);

  await b.close();
  process.exit(clean && !errs.length ? 0 : 1);
})();
