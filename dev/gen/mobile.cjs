/* Mobile audit runner.
   node dev/gen/mobile.cjs <url> [--sizes 390x844,360x740] [--out dev/gen/out/mob]
   Loads the page at each phone size, scrolls the whole thing a screen at a
   time, runs dev/gen/audit.js at every stop and merges what it finds, then
   saves a full-page picture per size. Prints JSON on stdout. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2);
const url = args[0] || 'http://localhost:8765/index.html';
const flag = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const sizes = (flag('--sizes') || '390x844,360x740,430x932').split(',').map(s => s.split('x').map(Number));
const outDir = flag('--out') || 'dev/gen/out/mob';
const waitMs = +(flag('--wait') || 1600);
const AUDIT = fs.readFileSync('dev/gen/audit.js', 'utf8');

const key = o => JSON.stringify(o);

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const report = { url, sizes: [] };
  for (const [w, h] of sizes) {
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(String(e.message).slice(0, 160)));
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 160)); });
    await p.goto(url, { waitUntil: 'load' });
    await p.waitForTimeout(waitMs);
    await p.addScriptTag({ content: AUDIT });

    const tag = `${w}x${h}`;
    const merged = { overlaps: [], cropped: [], broken: [], clipped: [], offscreen: [], tiny: [], tapTargets: [] };
    const seen = {}; for (const k in merged) seen[k] = new Set();
    let sideways = false, steps = 0;

    const total = await p.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < Math.max(total - h * 0.4, 1); y += Math.round(h * 0.8)) {
      await p.evaluate(v => scrollTo(0, v), y);
      await p.waitForTimeout(450);
      const r = await p.evaluate(l => window.__AUDIT(l), `y=${y}`);
      await p.screenshot({ path: path.join(outDir, `${tag}_${String(steps).padStart(2,'0')}.png`) });
      steps++;
      sideways = sideways || r.pageScrollsSideways;
      for (const k in merged) (r[k] || []).forEach(it => { const s = key(it); if (!seen[k].has(s)) { seen[k].add(s); merged[k].push({ ...it, at: `y=${y}` }); } });
    }
    await p.evaluate(() => scrollTo(0, 0));
    await p.waitForTimeout(300);
    await p.screenshot({ path: path.join(outDir, `full_${tag}.png`), fullPage: true });
    report.sizes.push({ viewport: tag, pageHeight: total, stops: steps, pageScrollsSideways: sideways, jsErrors: [...new Set(errs)], ...merged });
    await ctx.close();
  }
  await b.close();
  console.log(JSON.stringify(report, null, 1));
})().catch(e => { console.error('RUNNER FAILED:', e.message); process.exit(1); });
