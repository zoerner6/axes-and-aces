/* Re-render the logo at print resolution.
   node dev/gen/logo-print.cjs

   Everything in dev/gen/logo-out.html except the axe is live text and CSS
   gradients, so it redraws perfectly crisp at any size. The axe was the whole
   ceiling: art/i_eq_axe_5.webp is 384px and the wordmark shows it at 158 CSS
   px, which left only about 2.4x before it started upscaling - barely more than
   the shipped logo already had.

   store/brand/i_eq_axe_5_hi.png is the same axe redrawn at 2045px, which lifts that
   ceiling to roughly 12x. 6x is plenty: the wordmark lands near 3800px wide,
   against the 2550px of an 8.5x11 page at 300 DPI.

   The icon panes still use art/i_axe.webp at 384px, and the icon already shows
   it at 466 CSS px, so the icon cannot be enlarged this way without redrawing
   that axe too. The shipped 512px icons are fine for favicons and small print
   devices; redraw i_axe the same way if a big one is ever needed.

   Output goes to store/brand/, which netlify.toml keeps off the website. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = 'store/brand';
const PAGE = 'file://' + path.resolve('dev/gen/logo-out.html').replace(/\\/g, '/');
const HI_AXE = 'file://' + path.resolve('store/brand/i_eq_axe_5_hi.png').replace(/\\/g, '/');

/* name, hash, viewport, scale, clip to the plaque (with room for its shadow) */
const SHOTS = [
  ['logo-wide-print', 'wide',   { width: 1440, height: 638 }, 6, true],
  ['banner-print',    'banner', { width: 1200, height: 630 }, 4, false],
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  for (const [name, hash, viewport, scale, clipToBar] of SHOTS) {
    const ctx = await b.newContext({ viewport, deviceScaleFactor: scale });
    const p = await ctx.newPage();
    await p.goto(PAGE + '#' + hash, { waitUntil: 'load' });

    /* swap in the high-resolution axe; the page itself stays untouched */
    await p.evaluate(src => {
      document.querySelectorAll('.axe img').forEach(i => { i.src = src; });
    }, HI_AXE);

    /* the lettering IS the logo, so never shoot before the font has landed */
    await p.evaluate(() => document.fonts.ready);
    await p.waitForLoadState('networkidle').catch(() => {});
    await p.waitForTimeout(1500);

    const file = path.join(OUT, name + '.png');
    if (clipToBar) {
      /* an element screenshot cuts the drop shadow off at the border, so clip a
         padded box around it instead and keep the transparency */
      const box = await p.$eval('#m-wide', el => {
        const r = el.getBoundingClientRect();
        return { x: r.x, y: r.y, width: r.width, height: r.height };
      });
      const PAD = 34;
      await p.screenshot({
        path: file, omitBackground: true,
        clip: { x: box.x - PAD, y: box.y - PAD, width: box.width + PAD * 2, height: box.height + PAD * 2 },
      });
    } else {
      await p.screenshot({ path: file });
    }
    await ctx.close();

    const d = require('child_process')
      .execSync(`python -I -c "from PIL import Image;im=Image.open(r'${file}');print(im.size[0],'x',im.size[1])"`)
      .toString().trim();
    console.log(`${name.padEnd(17)} ${d.padEnd(14)} ${(fs.statSync(file).size / 1048576).toFixed(1)}MB`);
  }
  await b.close();
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
