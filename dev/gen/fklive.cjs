/* Is Monster Farkle actually live and working on the real site?
     node dev/gen/fklive.cjs

   Checks the things a deploy can get wrong that a local test cannot see: the
   page serving at all, its headers, its own icon and manifest, the share
   banner, the front-page link, and the leaderboard function answering on the
   new board. Then it opens the real page in a browser and plays a turn. */
const { chromium } = require('playwright');

const SITE = 'https://axesandaces.com';
const rows = [];
const ok = (name, pass, detail = '') => { rows.push({ name, pass, detail }); };

async function head(path, want) {
  try {
    const r = await fetch(SITE + path, { method: 'GET', redirect: 'follow' });
    const ct = r.headers.get('content-type') || '';
    const cc = r.headers.get('cache-control') || '';
    const body = want === 'text' ? await r.text() : null;
    return { status: r.status, ct, cc, body };
  } catch (e) { return { status: 0, err: String(e.message) }; }
}

(async () => {
  const page = await head('/farkle.html', 'text');
  ok('farkle.html serves', page.status === 200, `HTTP ${page.status}`);
  ok('farkle.html is not cached hard', /no-cache/.test(page.cc), page.cc || '(no header)');
  if (page.body) {
    ok('page carries its own manifest', page.body.includes('farkle.webmanifest'));
    ok('page carries its own icon', page.body.includes('icons/farkle-192.png'));
    ok('og:image is the Farkle banner', page.body.includes('b/farkle.jpg'));
    ok('the Axes & Aces word logo is NOT on it', !page.body.includes('logo-wide'));
    ok('the dice mark is in the page', page.body.includes('img/farkle-dice.webp'));
  }
  for (const [p, label] of [
    ['/farkle.webmanifest', 'manifest'],
    ['/icons/farkle-512.png', 'app icon'],
    ['/icons/farkle-maskable-512.png', 'maskable icon'],
    ['/img/farkle-dice.webp', 'dice art'],
    ['/img/farkle-emblem.webp', 'emblem'],
    ['/b/farkle.jpg', 'share banner'],
    ['/b/farkle_boss.html', 'a share page'],
  ]) {
    const r = await head(p);
    ok(`${label} serves (${p})`, r.status === 200, `HTTP ${r.status}`);
  }

  /* Netlify's pretty-URL post-processing rewrites href="farkle.html" to
     href="/farkle" at deploy time, so look for either and then prove whatever
     the link points at actually serves the game. */
  const front = await head('/', 'text');
  const linked = !!front.body && /href=['"]\/?farkle(\.html)?['"]/.test(front.body);
  ok('front page links to Farkle', linked);
  const clean = await head('/farkle', 'text');
  ok('the clean URL /farkle serves the game', clean.status === 200 && /rollBtn/.test(clean.body || ''), `HTTP ${clean.status}`);

  const lb = await head('/.netlify/functions/get-scores?board=farkle', 'text');
  let lbOk = false;
  try { lbOk = lb.status === 200 && Array.isArray(JSON.parse(lb.body).scores); } catch (e) {}
  ok('leaderboard answers on the farkle board', lbOk, `HTTP ${lb.status} ${String(lb.body).slice(0, 60)}`);

  /* and finally: does it actually play? */
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 120)); });
  await p.goto(SITE + '/farkle.html', { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  const started = await p.evaluate(() => !!document.querySelector('.fklogo, #rollBtn'));
  ok('the page boots', started);
  /* clear the opening story and roll once */
  for (let i = 0; i < 8; i++) {
    const btn = await p.$('#overlay:not([hidden]) [data-act="storyNext"], #overlay:not([hidden]) [data-act="newHero"], #overlay:not([hidden]) [data-act="fight"]');
    if (!btn) break;
    await btn.click().catch(() => {});
    await p.waitForTimeout(700);
  }
  const canRoll = await p.evaluate(() => { const b = document.getElementById('rollBtn'); return !!b && !b.disabled; });
  if (canRoll) {
    await p.click('#rollBtn');
    await p.waitForTimeout(2200);
    const faces = await p.evaluate(() => [...document.querySelectorAll('.die')].filter(d => !d.classList.contains('blank')).length);
    ok('the dice roll', faces > 0, `${faces} dice showing`);
  } else ok('the dice roll', false, 'Roll never became available');
  ok('no script errors on the live page', errs.length === 0, errs.slice(0, 2).join(' | '));
  await p.screenshot({ path: 'dev/gen/out/fk/live.png' });
  await b.close();

  console.log('');
  let bad = 0;
  for (const r of rows) {
    if (!r.pass) bad++;
    console.log(`${r.pass ? '  ok  ' : 'FAIL  '}${r.name.padEnd(42)}${r.detail}`);
  }
  console.log(bad ? `\n${bad} of ${rows.length} checks FAILED.` : `\nAll ${rows.length} checks pass. Monster Farkle is live.`);
  process.exit(bad ? 1 : 0);
})();
