/* Does every panel really fit, including off the TOP?
     node dev/gen/fkpanels.cjs

   The panel is a centred flex column. When its content is taller than the
   screen, the overflow goes both ways: the bottom can be scrolled to, and
   the top simply is not there. `scrollHeight - clientHeight` reads zero for
   the part that went off the top, so a check built on it reports a panel as
   fitting while its first line is gone. That is how a heading sat invisible
   above the closing panel at 320 and 375 while the spill measured 0px.

   So this measures every direct child against the panel's own box, in both
   directions, and says which line went missing. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
execFileSync('python', ['dev/gen/harness.py', 'dev/farkle.html', 'farkletest.html'], { stdio: 'inherit' });

const MIME = {'.html':'text/html','.js':'text/javascript','.webp':'image/webp','.png':'image/png',
  '.mp4':'video/mp4','.mp3':'audio/mpeg','.jpg':'image/jpeg','.css':'text/css'};

/* Every panel the game can put up, by the call that opens it. */
const PANELS = [
  ['how to play',      'helpPanel()'],
  ['the scoring table','guidePanel()'],
  ['the offer',        'tutorOffer()'],
  ['after the lesson', 'tutorDone()'],
  ['the menu',         'menuPanel()'],
  ['heroes',           'slotsPanel()'],
  ['the hall',         'lbPanel()'],
  ['save codes',       'cloudPanel()'],
  ['the merchant',     'shopPanel()'],
  ['potions',          'shopPanel("pots")'],
  ['charms',           'shopPanel("charms")'],
  ['the smith',        'shopPanel("smith")'],
  ['a level up',       'S.pendingLv=1; levelPanel()'],
  ['the fight intro',  'startFight()'],
];
const SIZES = [[390, 844], [375, 667], [360, 740], [320, 568]];

const rows = [];
(async () => {
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

  for (const [w, h] of SIZES) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const p = await ctx.newPage();
    await p.goto(base, { waitUntil: 'load' });
    await p.waitForTimeout(900);
    await p.evaluate(() => { try{ window.__FK.store.set('taught', true); }catch(e){} });
    for (const [name, open] of PANELS) {
      await p.evaluate(x => window.__A.ev('closePanel(); ' + x), open);
      await p.waitForTimeout(380);
      const m = await p.evaluate(() => {
        const pa = document.getElementById('panel');
        if (!pa || document.getElementById('overlay').hidden) return { none: true };
        const pr = pa.getBoundingClientRect();
        const lost = [];
        for (const el of pa.querySelectorAll(':scope > *')) {
          const r = el.getBoundingClientRect();
          if (!r.height) continue;
          const over = Math.round(pr.top - r.top), under = Math.round(r.bottom - pr.bottom);
          if (over > 1) lost.push(`off the top by ${over}px: "${(el.textContent || '').trim().slice(0, 30)}"`);
          else if (under > 1) lost.push(`off the bottom by ${under}px: "${(el.textContent || '').trim().slice(0, 30)}"`);
        }
        return { lost, scroll: pa.scrollHeight - pa.clientHeight };
      });
      if (m.none) { rows.push({ name, w, h, pass: true, detail: 'no panel' }); continue; }
      rows.push({ name, w, h, pass: m.lost.length === 0,
                  detail: m.lost.length ? m.lost.join('; ') : (m.scroll > 0 ? `scrolls ${m.scroll}px` : '') });
      if (m.scroll > 0) rows[rows.length - 1].pass = false;
    }
    await ctx.close();
  }
  await b.close(); srv.close();

  console.log('');
  let bad = 0;
  for (const r of rows) {
    if (!r.pass) bad++;
    if (!r.pass || process.env.VERBOSE)
      console.log(`${r.pass ? '  ok  ' : 'FAIL  '}${String(r.w + 'x' + r.h).padEnd(9)} ${r.name.padEnd(18)} ${r.detail}`);
  }
  console.log(bad ? `\n${bad} of ${rows.length} panel views lose a line.`
                  : `\nAll ${rows.length} panel views fit, top and bottom.`);
  process.exit(bad ? 1 : 0);
})();
