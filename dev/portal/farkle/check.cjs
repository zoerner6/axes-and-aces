/* Does the built package actually work?

     node dev/portal/farkle/check.cjs poki
     node dev/portal/farkle/check.cjs crazygames

   Serves dist/farkle-<portal>/ exactly as it would be served from a portal's
   CDN and then drives it. Everything here is asserted about behaviour, not
   about the text of the page: a patch that applied is not a game that plays,
   and a function that is defined is not a function that runs. That mistake
   has been made twice on this game already.

   What it proves:
     - nothing 404s and nothing throws, across a whole run
     - the SDK marks fire: loading finished, gameplay started
     - the ad break calls back even with no SDK on the page, which is what
       happens on a plain web server and whenever an ad fails to fill
     - a panel cancels the one before it, so no stale line lands in it
     - no page scroll and no panel that needs scrolling, at four phone sizes */
/* a bot has played before: take the one-time walk-through offer out
   of the way, the same as a returning player */
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const PORTAL = process.argv[2];
if (!['poki', 'crazygames'].includes(PORTAL)) {
  console.error('usage: node dev/portal/farkle/check.cjs <poki|crazygames>');
  process.exit(2);
}
const ROOT = path.join(__dirname, '..', '..', '..');
const DIST = path.join(ROOT, 'dist', 'farkle-' + PORTAL);
if (!fs.existsSync(DIST)) {
  console.error('No package at ' + DIST + ' - run build.py first.');
  process.exit(2);
}

/* Does this build carry the hall of heroes? Read it off the package rather
   than off the config, so the check is about what was actually built. */
const ONLINE = fs.readFileSync(path.join(DIST, 'index.html'), 'utf8')
  .includes("const API = 'https://axesandaces.com/.netlify/functions/'");

const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json',
  '.jpg':'image/jpeg','.woff2':'font/woff2','.webmanifest':'application/manifest+json'};

const rows = [];
const ok = (name, pass, detail = '') => rows.push({ name, pass, detail });

/* Console errors that belong to the portal's own ad stack, not to the game.
   Serving the package over plain http://127.0.0.1 makes the ad frames
   complain about COOP on an untrustworthy origin; on a real portal they are
   served over https and do not. Anything filtered out here is still printed
   at the end, because a check that hides what it found is worse than none. */
const NOT_OURS = /Cross-Origin-Opener-Policy|ERR_BLOCKED_BY_CLIENT|net::ERR_/;

/* Click through the DOM, not through the mouse. Both portals' SDKs lay their
   own full-screen loading panel over the game, and on a local server it never
   clears: the SDK cannot check the domain or fetch an ad, so it waits forever.
   A real mouse click lands on that panel; a DOM click reaches the button
   underneath, which is what we are here to test. On the portals themselves
   the panel clears as soon as gameLoadingFinished / loadingStop is called,
   and the check above proves the game calls it. */
const tap = (pg, sel) => pg.evaluate(s => {
  const el = document.querySelector(s);
  if (!el || el.disabled) return false;
  el.click(); return true;
}, sel);
const skipped = [];
function noteError(text, url) {
  const ours = !url || url.startsWith(SELF.base);
  if (!ours || NOT_OURS.test(text)) { skipped.push((url || '?') + ' :: ' + text.slice(0, 110)); return; }
  SELF.errs.push(text.slice(0, 140));
}
const SELF = { base: '', errs: [] };

/* The portal SDKs are not reachable from here and never will be during a
   local check, so every run is the "SDK blocked" case. That is the case that
   has to keep working: the game must play start to finish without one. */
function serve() {
  return http.createServer((q, r) => {
    const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
    const f = path.join(DIST, rel);
    if (!f.startsWith(DIST) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) {
      r.writeHead(404); return r.end('no');
    }
    /* content-length on purpose: the weight before the first playable frame
       is a number CrazyGames gate on, and it can only be counted for real if
       every response says how big it is. */
    r.writeHead(200, {
      'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream',
      'content-length': fs.statSync(f).size,
    });
    fs.createReadStream(f).pipe(r);
  });
}

(async () => {
  const srv = serve();
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/`;
  SELF.base = base;
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  /* ---------- 1. a whole run, watching for 404s and errors ---------- */
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const p = await ctx.newPage();
  const errs = SELF.errs, missing = [], offsite = [];
  p.on('pageerror', e => noteError(e.message, base));
  p.on('console', m => { if (m.type() === 'error') noteError(m.text(), (m.location() || {}).url); });
  /* Weigh what the player downloads before the game is playable. CrazyGames
     cap it at 50MB and want it under 20MB for their mobile home page, and
     the only honest way to know is to count the bytes over the wire up to
     the moment the SDK is told gameplay has started. */
  let bytes = 0, bytesAtPlay = -1;
  p.on('response', r => {
    if (r.status() >= 400) missing.push(r.status() + ' ' + r.url().replace(base, ''));
    if (r.url().startsWith(base)) bytes += Number(r.headers()['content-length'] || 0);
  });
  /* The portal's SDK is allowed to pull its whole ad stack in - that is what
     it is for, and on a real portal it will. What must never happen is the
     game asking a font CDN or Facebook for anything, and - unless this build
     carries the hall of heroes - the old site either. */
  const BANNED = ONLINE
    ? /fonts\.googleapis\.com|fonts\.gstatic\.com|facebook\.com/
    : /axesandaces\.com|fonts\.googleapis\.com|fonts\.gstatic\.com|facebook\.com/;
  p.on('request', r => { if (BANNED.test(r.url())) offsite.push(r.url()); });

  await p.goto(base, { waitUntil: 'load' });
  await p.evaluate(() => { try{ window.__FK.store.set('taught', true); }catch(e){} }).catch(() => {});
  await p.waitForTimeout(2500);
  ok('the page boots', await p.evaluate(() => !!document.getElementById('app')));
  ok('the game exposes its hooks', await p.evaluate(() => !!window.__FK && !!window.AA));

  /* clear the opening story */
  for (let i = 0; i < 14; i++) {
    const did = await tap(p, '#overlay:not([hidden]) [data-act="storyNext"], #overlay:not([hidden]) [data-act="fight"]');
    if (!did) break;
    await p.waitForTimeout(500);
  }

  bytesAtPlay = bytes;
  const marks = await p.evaluate(() => window.AA.marks);
  ok('the portal was told loading finished', marks.loaded > 0, marks.loaded ? marks.loaded.toFixed(0) + 'ms' : 'never');
  ok('the portal was told gameplay started', marks.firstPlay > 0, marks.firstPlay ? marks.firstPlay.toFixed(0) + 'ms' : 'never');
  const mb = bytesAtPlay / 2 ** 20;
  ok('under 50MB before the game is playable', mb < 50, `${mb.toFixed(1)}MB`
     + (mb < 20 ? ' - also under the 20MB their mobile home page wants' : ''));

  /* ---------- 2. the ad break must call back with no SDK ---------- */
  const adBack = await p.evaluate(() => new Promise(res => {
    const t = setTimeout(() => res('never called back'), 8000);
    window.AA.adBreak(() => { clearTimeout(t); res('ok'); });
  }));
  ok('the ad break calls back with no SDK on the page', adBack === 'ok', adBack);
  ok('an ad never leaves the game hidden',
     await p.evaluate(() => !document.documentElement.classList.contains('ad-playing')));

  /* ---------- 3. a new panel cancels the one before it ----------
     The fight intro schedules its typing with laterIn(). Open another panel
     straight after and the old timers must not write into it. This is the
     fix that was defined and never called: assert what lands on screen. */
  const stale = await p.evaluate(async () => {
    const F = window.__FK;
    F.startFight();                                  /* schedules the intro typing */
    await new Promise(r => setTimeout(r, 120));
    F.openPanel('<p id="encCap">KEEP</p><p id="encSay">KEEP</p>');
    await new Promise(r => setTimeout(r, 1800));     /* past both laterIn delays */
    const cap = document.getElementById('encCap'), say = document.getElementById('encSay');
    return { cap: cap && cap.textContent, say: say && say.textContent };
  });
  ok('no stale caption lands in the next panel', stale.cap === 'KEEP', 'reads ' + JSON.stringify(stale.cap));
  ok('no stale line lands in the next panel', stale.say === 'KEEP', 'reads ' + JSON.stringify(stale.say));

  ok('nothing 404s before the run', missing.length === 0, missing.slice(0, 3).join(' | '));
  await ctx.close();

  /* ---------- 4. play several fights for real ----------
     On its own page: the stale-timer test above replaces a fight intro with
     markup of its own, so that tab is left mid-fight with the intro never
     dismissed and the game rightly refuses to roll. */
  const ctx2 = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
  const q0 = await ctx2.newPage();
  q0.on('pageerror', e => noteError(e.message, base));
  q0.on('console', m => { if (m.type() === 'error') noteError(m.text(), (m.location() || {}).url); });
  q0.on('response', r => { if (r.status() >= 400) missing.push(r.status() + ' ' + r.url().replace(base, '')); });
  q0.on('request', r => { if (BANNED.test(r.url())) offsite.push(r.url()); });
  await q0.goto(base, { waitUntil: 'load' });
  await q0.evaluate(() => { try{ window.__FK.store.set('taught', true); }catch(e){} }).catch(() => {});
  await q0.waitForTimeout(2200);
  /* A bot that plays the way the game means you to: set aside the best split
     the game's own scoring finds, keep rolling while the wind is small, strike
     once it is worth landing. Striking at random banks nothing and never
     kills a monster, which looks exactly like a broken game. */
  let turns = 0, wins = 0, farkles = 0, stalled = '';
  const t0 = Date.now();
  while (Date.now() - t0 < 180000 && wins < 4) {
    const panel = await q0.evaluate(() => {
      const o = document.getElementById('overlay');
      if (!o || o.hidden) return null;
      const b = o.querySelector('[data-act="fight"], [data-act="onward"], [data-act="leaveShop"], '
        + '[data-act="storyNext"], [data-act="again"], [data-act="perk"], [data-act="dailyQuit"], '
        + '[data-act="close"]');
      if (b) { b.click(); return 'clicked'; }
      return 'no way out: ' + [...o.querySelectorAll('[data-act]')].map(x => x.dataset.act).join(',');
    });
    if (panel && panel !== 'clicked') { stalled = panel; break; }
    if (panel === 'clicked') { await q0.waitForTimeout(500); continue; }

    const can = await q0.evaluate(() => {
      const r = document.getElementById('rollBtn');
      return !!r && !r.disabled;
    });
    if (!can) { await q0.waitForTimeout(400); continue; }
    await tap(q0, '#rollBtn');
    await q0.waitForTimeout(520);
    for (let guard = 0; guard < 12; guard++) {
      const picked = await q0.evaluate(() => {
        const FK = window.__FK, roll = FK.rollIdx();
        if (!roll.length) return 'none';
        const best = FK.bestSplit(FK.facesOf(roll));
        if (!best.score) return 'farkle';
        best.keep.forEach(k => {
          const el = document.querySelector(`[data-die="${roll[k]}"]`);
          if (el && !el.disabled) el.click();
        });
        return 'kept';
      });
      if (picked !== 'kept') { if (picked === 'farkle') farkles++; break; }
      await q0.waitForTimeout(180);
      const st = await q0.evaluate(() => ({
        wind: +document.getElementById('windNum').textContent.replace(/,/g, ''),
        roll: !document.getElementById('rollBtn').disabled,
        strike: !document.getElementById('strikeBtn').disabled }));
      if (st.wind >= 300 || !st.roll) {
        if (st.strike) { await tap(q0, '#strikeBtn'); turns++; }
        break;
      }
      await tap(q0, '#rollBtn');
      await q0.waitForTimeout(760);
    }
    await q0.waitForTimeout(700);
    wins = await q0.evaluate(() => (window.__FK.S && window.__FK.S.wins) || 0);
  }
  ok('the game plays', turns > 3 && wins > 0 && !stalled,
     `${turns} strikes, ${farkles} farkles, ${wins} wins${stalled ? ' - STALLED: ' + stalled : ''}`);
  ok('nothing 404s in a whole run', missing.length === 0, missing.slice(0, 3).join(' | '));
  ok('nothing throws in a whole run', errs.length === 0, errs.slice(0, 2).join(' | '));
  const strayHosts = [...new Set(offsite.map(u => { try { return new URL(u).host; } catch (e) { return u; } }))];
  ok(ONLINE ? 'the game never asks a font CDN or Facebook for anything'
            : 'the game never asks the old site or a font CDN for anything',
     strayHosts.length === 0, strayHosts.join(', '));

  /* If the build carries the hall of heroes, prove it answers from a domain
     that is not ours - which is the whole question - rather than trusting a
     note that said it could not. CrazyGames serve the game from their own
     origin, so this is exactly the cross-origin call that has to work. */
  if (ONLINE) {
    const hall = await q0.evaluate(async () => {
      try {
        const r = await fetch('https://axesandaces.com/.netlify/functions/get-scores?board=farkle');
        if (!r.ok) return 'HTTP ' + r.status;
        const j = await r.json();
        return Array.isArray(j.scores) ? 'ok, ' + j.scores.length + ' names' : 'no scores array';
      } catch (e) { return 'blocked: ' + e.message; }
    });
    ok('the hall of heroes answers from another domain', hall.startsWith('ok'), hall);
  }
  await ctx2.close();

  /* ---------- 5. four phone sizes: nothing scrolls, nothing spills ---------- */
  for (const [w, h] of [[390, 844], [375, 667], [360, 740], [320, 568]]) {
    const c = await b.newContext({ viewport: { width: w, height: h }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const q = await c.newPage();
    await q.goto(base, { waitUntil: 'load' });
  await q.evaluate(() => { try{ window.__FK.store.set('taught', true); }catch(e){} }).catch(() => {});
    await q.waitForTimeout(1800);
    const m = await q.evaluate(() => {
      const d = document.documentElement;
      const panel = document.getElementById('panel');
      return {
        pageScroll: d.scrollHeight - d.clientHeight,
        sideScroll: d.scrollWidth - d.clientWidth,
        panelScroll: panel ? panel.scrollHeight - panel.clientHeight : 0,
        phoneCSS: matchMedia('(max-width:560px)').matches,
      };
    });
    ok(`${w}x${h}: the phone layout is on`, m.phoneCSS);
    ok(`${w}x${h}: the page does not scroll`, m.pageScroll <= 0 && m.sideScroll <= 0,
       `down ${m.pageScroll}px, across ${m.sideScroll}px`);
    ok(`${w}x${h}: the opening panel fits`, m.panelScroll <= 0, `spills ${m.panelScroll}px`);
    await q.screenshot({ path: path.join(ROOT, 'dev', 'gen', 'out', 'fk', `portal-${PORTAL}-${w}.png`) }).catch(() => {});
    await c.close();
  }

  await b.close(); srv.close();
  console.log('\n' + PORTAL);
  let bad = 0;
  for (const r of rows) {
    if (!r.pass) bad++;
    console.log(`${r.pass ? '  ok  ' : 'FAIL  '}${r.name.padEnd(48)}${r.detail}`);
  }
  if (skipped.length) {
    console.log(`\n${skipped.length} console message(s) left out, none from the game itself:`);
    [...new Set(skipped.map(s => s.replace(/^\S+ :: /, '')))].slice(0, 6)
      .forEach(s => console.log('  - ' + s));
  }
  console.log(bad ? `\n${bad} of ${rows.length} checks FAILED.` : `\nAll ${rows.length} checks pass.`);
  process.exit(bad ? 1 : 0);
})();
