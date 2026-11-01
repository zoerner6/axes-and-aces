/* Phone screen sweep for daily.html.
   node dev/gen/dailyscan.cjs [--sizes 390x844,375x667,360x740,320x568] [--out dev/gen/out/daily]
   Walks the puzzle through every state at every size, runs dev/gen/audit.js on
   each one and saves a screenshot. Expects a static server on 8777. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2);
const flag = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const sizes = (flag('--sizes') || '390x844,375x667,360x740,320x568').split(',').map(s => s.split('x').map(Number));
const outDir = flag('--out') || 'dev/gen/out/daily';
const AUDIT = fs.readFileSync('dev/gen/audit.js', 'utf8');
const URL = 'http://127.0.0.1:8777/daily.html';

/* a guess that is wrong, one that shares the quest, one that shares the creature */
const WRONGS = ['Ice Golem', 'Giant Spider', 'Cellar Ghoul', 'Sand Golem'];

const STATES = [
  ['01-start', []],
  ['02-two', WRONGS.slice(0, 2)],
  ['03-four', WRONGS.slice(0, 4)],
  ['04-won', WRONGS.slice(0, 3).concat(['@answer'])],
  ['05-lost', WRONGS.slice(0, 4).concat(['Crystal Golem'])],
  ['06-typing', ['@type:gol']],
];

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  let problems = 0;
  for (const [w, h] of sizes) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: w <= 560, hasTouch: w <= 560 });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(String(e)));
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });

    for (const [name, steps] of STATES) {
      await page.goto(URL, { waitUntil: 'networkidle' });
      await page.evaluate(() => localStorage.clear());
      await page.reload({ waitUntil: 'networkidle' });
      await page.waitForFunction(() => window.__DAILY && window.__DAILY.answer);
      await page.evaluate(list => {
        const ans = window.__DAILY.answer.name;
        const i = document.getElementById('guess');
        for (const s of list) {
          if (s.indexOf('@type:') === 0) {
            i.value = s.slice(6); i.dispatchEvent(new Event('input', { bubbles: true })); continue;
          }
          i.value = (s === '@answer' ? ans : s);
          i.dispatchEvent(new Event('input', { bubbles: true }));
          i.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
        }
      }, steps);
      await page.waitForTimeout(500);

      const mq = await page.evaluate(() => matchMedia('(max-width:560px)').matches);
      if (w <= 560 && !mq) { console.log('!! no phone CSS at', w); problems++; }

      const r = await page.evaluate(AUDIT + `;window.__AUDIT(${JSON.stringify(name)})`);
      const hit = ['overlaps', 'cropped', 'broken', 'clipped', 'offscreen', 'tiny', 'tapTargets']
        .filter(k => r[k] && r[k].length);
      if (hit.length || r.pageScrollsSideways) {
        problems++;
        console.log(`\n[${w}x${h}] ${name}`);
        if (r.pageScrollsSideways) console.log('   page scrolls sideways');
        hit.forEach(k => console.log('   ' + k + ': ' + JSON.stringify(r[k])));
      }
      await page.screenshot({ path: path.join(outDir, `${w}x${h}-${name}.png`), fullPage: true });
    }
    if (errs.length) { problems++; console.log(`\n[${w}x${h}] script errors:`, errs.slice(0, 5)); }
    await ctx.close();
  }
  await browser.close();
  console.log(problems ? `\n${problems} thing(s) to look at` : '\nclean');
})();
