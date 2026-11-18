/* Does Old Bram's walk-through actually walk you through it?
     node dev/gen/fktutor.cjs

   Plays the lesson the way a first-time player would - tapping only what is
   ringed - and checks at every step that the ring is on the right thing, the
   step it is on is the step it should be on, and the button it is not talking
   about cannot be pressed. Then it checks Skip, from the middle of the
   lesson, really does end it and leave an ordinary playable turn behind.

   It drives a built page, because dev/farkle.html is a fragment: without
   dev/build.py's head there is no viewport meta and every phone media query
   quietly reads false while the page still looks laid out. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
execFileSync('python', ['dev/gen/harness.py', 'dev/farkle.html', 'farkletest.html'], { stdio: 'inherit' });

const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
const rows = [];
const ok = (name, pass, detail = '') => rows.push({ name, pass, detail });

const tap = (p, sel) => p.evaluate(s => {
  const el = document.querySelector(s);
  if (!el || el.disabled) return false;
  el.click(); return true;
}, sel);

const look = p => p.evaluate(() => ({
  step: window.__FK.tutor ? window.__FK.tutor.i : null,
  ringed: [...document.querySelectorAll('.tut-point')].map(e => e.id || e.className.split(' ')[0]),
  say: (document.getElementById('windNote').textContent || '').slice(0, 58),
  roll: !document.getElementById('rollBtn').disabled,
  strike: !document.getElementById('strikeBtn').disabled,
  wind: +document.getElementById('windNum').textContent.replace(/,/g, ''),
  can: [...document.querySelectorAll('.die.can')].length,
  skipShown: !document.querySelector('.tool.skip').hidden,
  faces: [...document.querySelectorAll('.die')].map(e => (e.getAttribute('aria-label') || '').replace('Die showing ', '')),
}));

async function settle(p, pred, ms = 9000) {
  const t0 = Date.now();
  for (;;) {
    if (await p.evaluate(pred)) return true;
    if (Date.now() - t0 > ms) return false;
    await p.waitForTimeout(140);
  }
}

/* Every number the lesson says out loud, checked against the scoring the
   game actually uses. Copy drifting away from the mechanics it describes is
   its own kind of bug, and a silent one: the walk-through would still pass
   every behavioural check while teaching the wrong odds. It said "five
   times in six" once, and a single die farkles four. */
function copyMatchesTheRules() {
  const src = fs.readFileSync(path.join(ROOT, 'dev', 'farkle.html'), 'utf8');
  const block = src.match(/\/\* ===== SCORING =====[\s\S]*?\/\* ===== END SCORING ===== \*\//)[0];
  const F = new Function(block + '; return {isFarkle, scoreOf};')();
  const lesson = src.slice(src.indexOf('const LESSON = ['), src.indexOf('let tutor = null'));
  const says = n => lesson.indexOf(String(n)) >= 0;
  const miss = [1, 2, 3, 4, 5, 6].filter(f => F.isFarkle([f])).length;
  return [
    ['a 1 really is 100', F.scoreOf([1]) === 100 && says(100)],
    ['a 5 really is 50', F.scoreOf([5]) === 50 && says(50)],
    ['the pair really is 150', F.scoreOf([1, 5]) === 150 && says(150)],
    ['three 2s really are 200', F.scoreOf([2, 2, 2]) === 200 && says(200)],
    ['the total really is 350', F.scoreOf([1, 5]) + F.scoreOf([2, 2, 2]) === 350 && says(350)],
    ['one die really misses two throws in three', miss === 4
      && /two throws in three/.test(lesson)],
  ];
}

(async () => {
  for (const [what, pass] of copyMatchesTheRules()) ok('the lesson is telling the truth: ' + what, pass);

  const srv = http.createServer((q, r) => {
    const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/, '') || 'farkletest.html';
    const f = path.join(ROOT, rel);
    if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end('no'); }
    r.writeHead(200, { 'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(r);
  });
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const b = await chromium.launch();

  /* ---------- 1. a first-time player is offered it, once ---------- */
  {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const p = await ctx.newPage();
    await p.goto(base, { waitUntil: 'load' });
    await p.waitForTimeout(1200);
    for (let i = 0; i < 12; i++) {
      if (!await tap(p, '#overlay:not([hidden]) [data-act="storyNext"]')) break;
      await p.waitForTimeout(400);
    }
    await tap(p, '#overlay:not([hidden]) [data-act="fight"]');
    await p.waitForTimeout(700);
    const offered = await p.evaluate(() =>
      !!document.querySelector('#overlay:not([hidden]) [data-act="tutor"]'));
    ok('a first-time player is offered the walk-through', offered);
    /* and declining it is remembered */
    await tap(p, '[data-act="tutorNo"]');
    await p.waitForTimeout(300);
    ok('declining it closes the panel', await p.evaluate(() => document.getElementById('overlay').hidden));
    ok('and it is remembered', await p.evaluate(() => window.__FK.store.get('taught', false)));
    await ctx.close();
  }

  /* ---------- 2. the lesson itself, tapping only what is ringed ---------- */
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 120)); });
  await p.goto(base, { waitUntil: 'load' });
  await p.waitForTimeout(1200);
  await p.evaluate(() => { window.__FK.S.introBeat = 9; window.__FK.closePanel(); window.__FK.startFight(); });
  await p.waitForTimeout(900);
  await tap(p, '#overlay:not([hidden]) [data-act="fight"]');
  await p.waitForTimeout(500);
  await p.evaluate(() => window.__FK.tutorStart());
  await p.waitForTimeout(500);

  let s = await look(p);
  ok('step 1 rings Roll', s.step === 0 && s.ringed.includes('rollBtn'), `step ${s.step}, ringed ${s.ringed}`);
  ok('Skip is on screen from the first step', s.skipShown);
  ok('Strike cannot be pressed yet', !s.strike);

  await tap(p, '#rollBtn');
  await settle(p, () => window.__FK.tutor && window.__FK.tutor.i === 1);
  s = await look(p);
  ok('the hand is dealt, not chanced', s.faces.join('') === '153346', s.faces.join(' '));
  ok('step 2 rings the dice that score', s.step === 1 && s.ringed.filter(x => x === 'die').length === 2,
     `step ${s.step}, ${s.ringed.length} ringed`);
  ok('only the 1 and the 5 are tappable', s.can === 2, `${s.can} lit`);
  ok('neither button can be pressed mid-step', !s.roll && !s.strike);

  /* tap exactly what is ringed, as a player would */
  await p.evaluate(() => [...document.querySelectorAll('.die.tut-point')].forEach(e => e.click()));
  await settle(p, () => window.__FK.tutor && window.__FK.tutor.i === 2);
  s = await look(p);
  ok('setting both aside is worth 150', s.wind === 150, `${s.wind}`);
  ok('step 3 rings Roll again', s.step === 2 && s.ringed.includes('rollBtn'), `step ${s.step}`);
  ok('Strike is held back at step 3', !s.strike);

  await tap(p, '#rollBtn');
  await settle(p, () => window.__FK.tutor && window.__FK.tutor.i === 3);
  s = await look(p);
  ok('the second hand is dealt too', s.faces.filter(f => f === '2').length === 3, s.faces.join(' '));
  ok('step 4 rings the three 2s', s.step === 3 && s.ringed.filter(x => x === 'die').length === 3,
     `step ${s.step}, ${s.ringed.filter(x => x === 'die').length} ringed`);

  await p.evaluate(() => [...document.querySelectorAll('.die.tut-point')].forEach(e => e.click()));
  await settle(p, () => window.__FK.tutor && window.__FK.tutor.i === 4);
  s = await look(p);
  ok('three 2s take it to 350', s.wind === 350, `${s.wind}`);
  ok('step 5 rings Strike', s.step === 4 && s.ringed.includes('strikeBtn'), `step ${s.step}`);
  ok('Roll is held back on the last step', !s.roll);

  await tap(p, '#strikeBtn');
  await settle(p, () => !window.__FK.tutor, 12000);
  ok('the lesson ends when the blow lands', await p.evaluate(() => !window.__FK.tutor));
  const ended = await settle(p, () =>
    !!document.querySelector('#overlay:not([hidden]) .guide'), 12000);
  ok('it finishes on the scoring table', ended);
  ok('nothing is left ringed', await p.evaluate(() => !document.querySelector('.tut-point')));
  ok('the Skip button is put away', await p.evaluate(() => document.querySelector('.tool.skip').hidden));
  ok('no script errors through the whole lesson', errs.length === 0, errs.slice(0, 2).join(' | '));
  await ctx.close();

  /* ---------- 3. Skip, from the middle, really stops it ---------- */
  {
    const c = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const q = await c.newPage();
    await q.goto(base, { waitUntil: 'load' });
    await q.waitForTimeout(1200);
    await q.evaluate(() => { window.__FK.S.introBeat = 9; window.__FK.closePanel(); window.__FK.startFight(); });
    await q.waitForTimeout(900);
    await tap(q, '#overlay:not([hidden]) [data-act="fight"]');
    await q.waitForTimeout(400);
    await q.evaluate(() => window.__FK.tutorStart());
    await q.waitForTimeout(400);
    await tap(q, '#rollBtn');
    await settle(q, () => window.__FK.tutor && window.__FK.tutor.i === 1);
    await tap(q, '.tool.skip');
    await q.waitForTimeout(500);
    const after = await look(q);
    ok('Skip ends the lesson on the spot', after.step === null);
    ok('Skip leaves nothing ringed', after.ringed.length === 0, after.ringed.join(','));
    ok('Skip puts the ordinary line back', /set aside/i.test(after.say), after.say);
    /* and the turn it leaves behind is a real one you can keep playing */
    await q.evaluate(() => [...document.querySelectorAll('.die.can')].forEach(e => e.click()));
    await q.waitForTimeout(300);
    const playable = await look(q);
    ok('and the turn is still playable', playable.roll || playable.strike,
       `roll ${playable.roll}, strike ${playable.strike}`);
    const random = await q.evaluate(async () => {
      document.getElementById('rollBtn').click();
      await new Promise(z => setTimeout(z, 900));
      return [...document.querySelectorAll('.die')].map(e => (e.getAttribute('aria-label') || '').slice(-1)).join('');
    });
    ok('the dice go back to chance after a skip', random.length === 6, random);
    await c.close();
  }

  /* ---------- 3b. asked for with no monster up, it says so instead of throwing ----------
     The ? is reachable whenever a panel is not covering it, and the lesson
     ends on a real strike, which needs something to hit. */
  {
    const c = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    const q = await c.newPage();
    const boom = [];
    q.on('pageerror', e => boom.push(e.message));
    await q.goto(base, { waitUntil: 'load' });
    await q.waitForTimeout(1200);
    await q.evaluate(() => { window.__FK.S.fight = null; window.__FK.closePanel(); window.__FK.tutorStart(); });
    await q.waitForTimeout(600);
    ok('with no monster up it declines rather than starting',
       await q.evaluate(() => !window.__FK.tutor));
    ok('and it says why', await q.evaluate(() =>
       !!document.querySelector('.toast') && /monster is up/i.test(document.querySelector('.toast').textContent)));
    ok('and nothing throws', boom.length === 0, boom.slice(0, 2).join(' | '));
    await c.close();
  }

  /* ---------- 4. it must not make a small phone scroll ---------- */
  for (const [w, h] of [[390, 844], [375, 667], [360, 740], [320, 568]]) {
    const c = await b.newContext({ viewport: { width: w, height: h }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const q = await c.newPage();
    await q.goto(base, { waitUntil: 'load' });
    await q.waitForTimeout(1100);
    await q.evaluate(() => { window.__FK.S.introBeat = 9; window.__FK.closePanel(); window.__FK.startFight(); });
    await q.waitForTimeout(800);
    await tap(q, '#overlay:not([hidden]) [data-act="fight"]');
    await q.waitForTimeout(300);
    await q.evaluate(() => window.__FK.tutorStart());
    await q.waitForTimeout(400);
    /* the wordiest step is the last one, so measure there */
    await tap(q, '#rollBtn');
    await settle(q, () => window.__FK.tutor && window.__FK.tutor.i === 1);
    await q.evaluate(() => [...document.querySelectorAll('.die.tut-point')].forEach(e => e.click()));
    await settle(q, () => window.__FK.tutor && window.__FK.tutor.i === 2);
    await tap(q, '#rollBtn');
    await settle(q, () => window.__FK.tutor && window.__FK.tutor.i === 3);
    await q.evaluate(() => [...document.querySelectorAll('.die.tut-point')].forEach(e => e.click()));
    await settle(q, () => window.__FK.tutor && window.__FK.tutor.i === 4);
    const m = await q.evaluate(() => {
      const d = document.documentElement;
      const die = document.querySelector('.die').getBoundingClientRect();
      const bar = document.querySelector('.top').getBoundingClientRect();
      return { down: d.scrollHeight - d.clientHeight, across: d.scrollWidth - d.clientWidth,
               die: Math.round(die.height), barRows: Math.round(bar.height),
               phoneCSS: matchMedia('(max-width:560px)').matches };
    });
    ok(`${w}x${h}: the phone layout is on`, m.phoneCSS);
    ok(`${w}x${h}: nothing scrolls on the wordiest step`, m.down <= 0 && m.across <= 0,
       `down ${m.down}px, across ${m.across}px`);
    ok(`${w}x${h}: the dice stay a real tap target`, m.die >= 44, `${m.die}px`);
    await q.screenshot({ path: `dev/gen/out/fk/tutor-${w}.png` });
    await c.close();
  }

  await b.close(); srv.close();
  console.log('');
  let bad = 0;
  for (const r of rows) {
    if (!r.pass) bad++;
    console.log(`${r.pass ? '  ok  ' : 'FAIL  '}${r.name.padEnd(48)}${r.detail}`);
  }
  console.log(bad ? `\n${bad} of ${rows.length} checks FAILED.` : `\nAll ${rows.length} checks pass.`);
  process.exit(bad ? 1 : 0);
})();
