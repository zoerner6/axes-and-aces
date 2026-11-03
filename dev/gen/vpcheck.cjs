/* Is the viewport real on a built test page?
   node <this> <page.html>
   If max-width:560px reads false at 320 wide, the page was built without the
   viewport meta and no phone CSS in the source is live. */
const { chromium } = require('playwright');
const path = require('path');

const page = path.resolve(process.argv[2] || 'soltest.html').replace(/\\/g, '/');

(async () => {
  const b = await chromium.launch();
  for (const [w, h] of [[320, 568], [360, 740], [375, 667], [390, 844], [900, 700]]) {
    const ctx = await b.newContext({
      viewport: { width: w, height: h }, deviceScaleFactor: 2,
      isMobile: w <= 560, hasTouch: w <= 560,
    });
    const p = await ctx.newPage();
    await p.goto('file://' + page, { waitUntil: 'load' });
    const r = await p.evaluate(() => ({
      iw: innerWidth,
      m560: matchMedia('(max-width:560px)').matches,
      phone: getComputedStyle(document.documentElement).getPropertyValue('--phone').trim(),
      sideways: document.documentElement.scrollWidth > innerWidth + 1,
    }));
    const ok = (w <= 560) === r.m560 && r.iw === w;
    console.log(`${String(w).padStart(4)}x${h}  innerWidth=${String(r.iw).padStart(4)}  ` +
      `max-width:560px=${String(r.m560).padEnd(5)}  --phone='${r.phone}'  ` +
      `sideways=${r.sideways}  ${ok ? 'OK' : '*** WRONG ***'}`);
    await ctx.close();
  }
  await b.close();
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
