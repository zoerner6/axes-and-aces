/* Does Monster Solitaire hold together on a real screen?

   node dev/gen/slscan.cjs [--shot out.png] [--widths 320x568,390x844]

   Builds the page, injects dev/gen/audit.js and an eval hook inside the game's
   IIFE, then loads it at every size that matters and reports what a person
   would actually notice: text on text, art sliced by its frame, words cut off,
   tap targets under 44px, and - the one this game can get wrong in a way the
   others cannot - the monster squeezed out by the board, or the board squeezed
   out by the monster.

   The eval hook has to go INSIDE the IIFE or nothing in the game's scope is
   reachable; see dev/gen/audit.js and the note above __A below. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const args = process.argv.slice(2);
const flag = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const shotAt = flag('--shot', null);

const SIZES = flag('--widths',
  '320x568,360x740,375x667,390x844,430x932,820x600,1024x768,1280x800')
  .split(',').map(s => s.split('x').map(Number));

/* ---- build a page with the auditor in it ---- */
execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
const built = fs.readFileSync(path.join(ROOT, 'solitaire.html'), 'utf8');
const audit = fs.readFileSync(path.join(ROOT, 'dev/gen/audit.js'), 'utf8');

/* The game is one IIFE. The hook is inserted before its closing `})();` so the
   scan can call into the game's own scope - startFight, S, R - instead of
   playing forward to every screen by hand. */
const close = built.lastIndexOf('})();');
if (close < 0) { console.error('FAILED: could not find the end of the game IIFE'); process.exit(1); }
const page = built.slice(0, close) +
  '\nObject.assign(window, { __A: { ev: x => eval(x) } });\n' +
  built.slice(close) +
  `\n<script>${audit}</script>\n`;

const out = path.join(ROOT, 'soltest.html');     /* gitignored, like playtest.html */
fs.writeFileSync(out, page);

const PLAIN = s => String(s).replace(/\s+/g, ' ').trim();

(async () => {
  const b = await chromium.launch();
  let bad = 0;

  for (const [w, h] of SIZES) {
    const ctx = await b.newContext({
      viewport: { width: w, height: h }, deviceScaleFactor: 2,
      isMobile: w <= 560, hasTouch: w <= 560,
    });
    const p = await ctx.newPage();
    await p.route('**/vid/**', r => r.abort());   /* 585MB of clips, and the stills are what we measure */
    const errs = [];
    p.on('pageerror', e => errs.push(PLAIN(e.message).slice(0, 150)));
    /* the clips are blocked above on purpose, so their failures are ours */
    const mine = t => /ERR_FAILED|ERR_ABORTED|vid\//.test(t);
    p.on('console', m => { if (m.type() === 'error' && !mine(m.text())) errs.push(PLAIN(m.text()).slice(0, 150)); });
    await p.goto('file://' + out.replace(/\\/g, '/'), { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(500);
    /* A fight opens behind its intro and the board is what is being measured,
       so press the button rather than hiding the panel: the button also hands
       the board back, and hiding the panel alone leaves it frozen. */
    await p.click('[data-act="fight"]', { timeout: 4000 }).catch(() => {});
    await p.waitForTimeout(160);
    /* The pouch row only exists when you are carrying something, and it is
       the one strip that can push the board off a short screen, so measure
       the screen a player who has been shopping actually sees. */
    await p.evaluate(() => {
      const SOL = window.__SOL, S = SOL.S;
      S.pots = ['heal', 'iron', 'rage'];
      S.ironskin = true; S.rage = true;
      SOL.renderPots();
    });
    await p.waitForTimeout(120);

    const m = await p.evaluate(() => {
      const PLAIN = s => String(s).replace(/\s+/g, ' ').trim();   /* the page has its own copy */
      const box = s => { const e = document.querySelector(s); if (!e) return null;
        const r = e.getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height),
          top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right) }; };
      const stage = box('#stage'), peaks = box('.peaks'), table = box('.table'), hero = box('.hero');
      /* The monster's head is the top third of the ART, not of the box: the
         name and the level badge live along the top of the stage on purpose,
         the same as in dev/farkle.html, and they sit above the picture rather
         than on it. What must stay clear is the picture's own head. */
      const pic = document.querySelector('#foePic img');
      const pr = pic ? pic.getBoundingClientRect() : null;
      const head = pr && { left: pr.left + pr.width * .22, right: pr.right - pr.width * .22,
                           top: pr.top, bottom: pr.top + pr.height * .36 };
      const over = !head ? [] : [...document.querySelectorAll('#stage *, #app > *')].filter(e => {
        const cs = getComputedStyle(e);
        if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false;
        if (!(e.textContent || '').trim() && e.tagName !== 'IMG') return false;
        if (e.closest('#foePic') || e.closest('.foe-vidwrap')) return false;
        if (e.contains(pic)) return false;          /* a box the art sits inside is not on top of it */
        const r = e.getBoundingClientRect();
        return r.left < head.right && r.right > head.left && r.top < head.bottom && r.bottom > head.top;
      }).map(e => (e.id || e.className || e.tagName) + ':' + PLAIN((e.textContent || e.src || '')).slice(0, 24));

      /* What object-fit:cover will do to a 16:9 clip in this box. Arithmetic,
         so it needs no clip loaded - and it is the number that decides whether
         the idle clip keeps the monster's head, which is the one thing the
         stills cannot tell us. */
      const sb = document.querySelector('#stage').getBoundingClientRect();
      const boxR = sb.width / sb.height, srcR = 16 / 9;
      const cut = boxR > srcR
        ? { what: 'top and bottom', pc: Math.round((1 - srcR / boxR) * 100) }
        : { what: 'the sides',      pc: Math.round((1 - boxR / srcR) * 100) };
      /* every control a thumb has to find */
      const taps = [...document.querySelectorAll('.tool, .pk.free, [data-act="turn"]')].map(e => {
        const r = e.getBoundingClientRect();
        return { what: e.dataset.act || e.textContent.trim().slice(0, 10) || 'card',
                 min: Math.round(Math.min(r.width, r.height)) };
      });
      return {
        stage, peaks, table, hero,
        headOver: over,
        smallTaps: taps.filter(t => t.min < 44),
        clipCut: cut,
        sideways: document.documentElement.scrollWidth > innerWidth + 1,
        tall: document.documentElement.scrollHeight > innerHeight + 1,
        foe: (document.querySelector('#foeName') || {}).textContent,
        audit: window.__AUDIT('solitaire'),
      };
    });

    const a = m.audit;
    const notes = [];
    if (!m.stage || m.stage.h < 100) { notes.push(`monster band only ${m.stage ? m.stage.h : 0}px`); bad++; }
    if (!m.peaks || m.peaks.h < 90) { notes.push(`peaks only ${m.peaks ? m.peaks.h : 0}px`); bad++; }
    if (m.sideways) { notes.push('scrolls sideways'); bad++; }
    if (m.tall) { notes.push(`page is ${document ? '' : ''}taller than the screen`); bad++; }
    if (m.headOver.length) { notes.push('over the monster head: ' + m.headOver.join(' | ')); bad++; }
    if (m.smallTaps.length) { notes.push('under 44px: ' + m.smallTaps.map(t => `${t.what} ${t.min}`).join(', ')); bad++; }
    if (a.overlaps.length) { notes.push('text on text: ' + a.overlaps.map(o => `"${o.a}" x "${o.b}" ${o.cover}`).join(' | ')); bad++; }
    if (a.cropped.length) { notes.push('art sliced: ' + a.cropped.map(c => `${c.src} ${c.box} sides ${c.cutSides} topbottom ${c.cutTopBottom}`).join(' | ')); bad++; }
    if (a.broken.length) { notes.push('missing art: ' + a.broken.join(', ')); bad++; }
    if (a.clipped && a.clipped.length) { notes.push('clipped text: ' + a.clipped.map(c => PLAIN(c.text || c)).join(' | ')); bad++; }
    if (a.tiny && a.tiny.length) { notes.push('tiny type: ' + a.tiny.map(t => PLAIN(t.text || t)).join(' | ')); bad++; }
    if (errs.length) { notes.push('JS: ' + [...new Set(errs)].join(' | ')); bad++; }

    console.log(`${String(w).padStart(4)}x${h}  monster ${String(m.stage.h).padStart(3)}px  ` +
      `peaks ${String(m.peaks.h).padStart(3)}px  table ${m.table ? m.table.h : '-'}  hero ${m.hero ? m.hero.h : '-'}  ` +
      `foe "${PLAIN(m.foe)}"  clip cuts ${m.clipCut.pc}% off ${m.clipCut.what}`);
    notes.forEach(n => console.log('      ** ' + n));

    if (shotAt) await p.screenshot({ path: shotAt.replace('.png', `_${w}.png`) });
    await ctx.close();
  }
  await b.close();
  console.log(bad ? `\n${bad} problems` : '\nnothing to report');
  if (bad) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
