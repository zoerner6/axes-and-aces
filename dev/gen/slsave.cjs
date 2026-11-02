/* Does a hero survive, and can it never tread on another game's?

   node dev/gen/slsave.cjs

   Three things are checked, and one is deliberately not.

   Checked: a hero written to a slot comes back after a reload; three slots
   hold three different heroes; and nothing Monster Solitaire writes touches a
   key belonging to Axes & Aces or Monster Farkle, which is the whole reason
   for the sl_ prefix.

   Also checked, against a stub rather than the live site: that a cloud save
   posts to save-game with an SL-prefixed code and that loading that code puts
   the hero back. The stub is on purpose. The real endpoint writes a row to
   Josh's database, and a test should not leave litter in it to prove a shape
   it can prove locally.

   NOT checked: that the deployed get-scores accepts "solitaire". It does not
   yet - the two board names were added to the function in this branch and the
   site has not been published - so the live one falls back to the daily
   board. That is a publish, not a bug. */
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
  await p.route('**/music/**', r => r.abort());

  /* a stand-in for the cloud, so nothing is written to the real one */
  const cloud = new Map();
  let lastSaveCode = null;
  await p.route('**/.netlify/functions/**', async route => {
    const u = new URL(route.request().url());
    const fn = u.pathname.split('/').pop();
    if (fn === 'save-game') {
      const body = JSON.parse(route.request().postData() || '{}');
      lastSaveCode = body.code;
      cloud.set(body.code, body.data);
      return route.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' });
    }
    if (fn === 'load-game') {
      const code = u.searchParams.get('code');
      const data = cloud.get(code);
      return route.fulfill({ status: data ? 200 : 404, contentType: 'application/json',
        body: JSON.stringify(data ? { data } : { error: 'No save found for that code' }) });
    }
    return route.fulfill({ status: 200, contentType: 'application/json', body: '{"scores":[]}' });
  });

  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message).replace(/\s+/g, ' ').slice(0, 150)));
  await p.goto('file://' + file, { waitUntil: 'load' });
  await p.waitForTimeout(400);
  await openGame(p);

  let bad = 0;
  const check = (name, ok, detail) => {
    if (!ok) bad++;
    console.log(`  ${name.padEnd(30)} ${ok ? 'holds' : '*** DOES NOT HOLD ***'}   ${detail}`);
  };

  /* ---- three slots, three heroes ---- */
  await p.evaluate(() => {
    const SOL = window.__SOL;
    [1, 2, 3].forEach(n => {
      SOL.SLOT = n;                       /* the game's slot, not just the stored one */
      localStorage.setItem('sl_slot', JSON.stringify(n));
      SOL.S = Object.assign(SOL.freshHero(), { name: 'Hero' + n, level: n * 4, gold: n * 11, world: n - 1 });
      SOL.saveGame();
    });
  });
  const slots = await p.evaluate(() => [1, 2, 3].map(n => {
    const v = JSON.parse(localStorage.getItem('sl_save_' + n) || 'null');
    return v && v.S ? `${v.S.name} lv${v.S.level}` : 'empty';
  }));
  check('three slots', new Set(slots).size === 3 && !slots.includes('empty'), slots.join(', '));

  /* ---- nothing of anyone else's was touched ---- */
  const keys = await p.evaluate(() => {
    /* plant a hero for each of the other two games and see if we tread on it */
    localStorage.setItem('aa_save_1', 'the card game');
    localStorage.setItem('fk_save_1', 'the dice game');
    const SOL = window.__SOL;
    SOL.S = Object.assign(SOL.freshHero(), { name: 'Intruder', level: 9 });
    SOL.saveGame();
    SOL.saveGame();
    return {
      aa: localStorage.getItem('aa_save_1'),
      fk: localStorage.getItem('fk_save_1'),
      mine: Object.keys(localStorage).filter(k => k.startsWith('sl_')).sort().join(', '),
      theirs: Object.keys(localStorage).filter(k => !k.startsWith('sl_')).sort().join(', ')
    };
  });
  check('other games left alone', keys.aa === 'the card game' && keys.fk === 'the dice game',
    `theirs: ${keys.theirs}`);
  check('its own keys all sl_', /^sl_/.test(keys.mine.split(', ')[0] || ''), keys.mine);

  /* ---- a hero survives a reload ---- */
  await p.evaluate(() => {
    const SOL = window.__SOL;
    SOL.SLOT = 2;
    localStorage.setItem('sl_slot', JSON.stringify(2));
    SOL.S = Object.assign(SOL.freshHero(), { name: 'Returned', level: 7, gold: 44, area: 2, step: 6 });
    SOL.saveGame();
  });
  await p.reload({ waitUntil: 'load' });
  await p.waitForTimeout(500);
  const back = await p.evaluate(() => {
    /* the slot screen is what a returning player meets */
    const rows = [...document.querySelectorAll('[data-act="loadHero"]')].map(e => e.textContent.replace(/\s+/g, ' ').trim());
    const two = document.querySelector('[data-act="loadHero"][data-slot="2"]');
    if (two) two.click();
    return { rows, clicked: !!two };
  });
  await p.waitForTimeout(400);
  const loaded = await p.evaluate(() => ({ name: window.__SOL.S.name, level: window.__SOL.S.level, gold: window.__SOL.S.gold }));
  check('a hero survives a reload', loaded.name === 'Returned' && loaded.level === 7 && loaded.gold === 44,
    `${loaded.name} level ${loaded.level}, ${loaded.gold} gold; the slot screen offered: ${back.rows.join(' / ')}`);

  /* ---- the cloud round trip, against the stub ---- */
  await openGame(p);
  const trip = await p.evaluate(async () => {
    const SOL = window.__SOL;
    SOL.S = Object.assign(SOL.freshHero(), { name: 'Cloudy', level: 12, gold: 77 });
    SOL.cloudPanel();
    document.querySelector('[data-act="cloudSave"]').click();
    await new Promise(r => setTimeout(r, 500));
    const code = document.querySelector('.cloud-code').textContent.trim();
    /* now be a different device: wipe the hero and type the code in */
    SOL.S = SOL.freshHero();
    SOL.cloudPanel();
    document.getElementById('cloudIn').value = code;
    document.querySelector('[data-act="cloudLoad"]').click();
    await new Promise(r => setTimeout(r, 700));
    return { code, name: SOL.S.name, level: SOL.S.level, gold: SOL.S.gold };
  });
  check('a code brings the hero back', trip.name === 'Cloudy' && trip.level === 12 && trip.gold === 77,
    `${trip.code} -> ${trip.name} level ${trip.level}, ${trip.gold} gold`);
  check('the code is Solitaire\'s own', (lastSaveCode || '').startsWith('SL'),
    `posted as ${String(lastSaveCode).slice(0, 6)}...`);

  console.log(errs.length ? `\nERRORS: ${[...new Set(errs)].join(' | ')}` : '\nno page errors');
  await b.close();
  if (bad || errs.length) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
