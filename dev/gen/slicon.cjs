/* Draw Monster Solitaire's app icon and write the four files the page and the
   manifest ask for.

   node dev/gen/slicon.cjs

   icons/sol-192.png and icons/sol-180.png are in the page head and
   icons/sol-192, -512 and -maskable-512 are in solitaire.webmanifest, so
   until these exist every single page load is a 404 - which is how this was
   found, in the sweep, rather than by anybody looking at a tab.

   BRAND.md's rule for a sister product: its own object, the same gold slab
   treatment, never the parent's wordmark. The object here is the three peaks,
   so that is what the icon is - three cards standing in a peak on the same
   soot and gold the game is built from. Drawn on a canvas, so it costs
   nothing and can be redrawn at any size later.

   The maskable one keeps everything inside the middle 80%, because a maskable
   icon is cropped to whatever shape the launcher feels like. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = path.join(ROOT, 'icons');
fs.mkdirSync(OUT, { recursive: true });

const FILES = [
  ['sol-512.png', 512, false],
  ['sol-192.png', 192, false],
  ['sol-180.png', 180, false],
  ['sol-maskable-512.png', 512, true],
];

const DRAW = `(size, maskable) => {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const x = c.getContext('2d');
  const S = size / 512;                     /* everything below is drawn at 512 */

  /* the table: soot, with the same warm glow the game's background has */
  x.fillStyle = '#14100d';
  x.fillRect(0, 0, size, size);
  const g = x.createRadialGradient(256 * S, 40 * S, 10 * S, 256 * S, 300 * S, 420 * S);
  g.addColorStop(0, 'rgba(242,182,50,.34)');
  g.addColorStop(1, 'rgba(242,182,50,0)');
  x.fillStyle = g;
  x.fillRect(0, 0, size, size);

  /* three cards in a peak. Inside the middle 80% when it has to survive a
     launcher deciding to crop it into a circle. */
  const k = maskable ? 0.78 : 1;
  x.save();
  x.translate(256 * S, 268 * S);
  x.scale(k, k);
  x.translate(-256 * S, -268 * S);

  const card = (cx, cy, rot, w, h) => {
    x.save();
    x.translate(cx * S, cy * S);
    x.rotate(rot);
    x.fillStyle = 'rgba(0,0,0,.55)';
    rr(x, (-w / 2 + 9) * S, (-h / 2 + 11) * S, w * S, h * S, 16 * S); x.fill();
    x.fillStyle = '#fffaf0';
    x.strokeStyle = '#000';
    x.lineWidth = 13 * S;
    rr(x, -w / 2 * S, -h / 2 * S, w * S, h * S, 16 * S);
    x.fill(); x.stroke();
    x.restore();
  };
  function rr(ctx, X, Y, W, H, R){
    ctx.beginPath();
    if(ctx.roundRect) ctx.roundRect(X, Y, W, H, R);
    else ctx.rect(X, Y, W, H);
  }

  card(150, 300, -0.22, 150, 210);          /* left */
  card(362, 300,  0.22, 150, 210);          /* right */
  card(256, 250,  0,    158, 222);          /* the tip, in front */

  /* one red pip on the front card, so it reads as cards and not as paper */
  x.fillStyle = '#c8161d';
  x.font = (108 * S) + 'px Georgia, serif';
  x.textAlign = 'center';
  x.textBaseline = 'middle';
  x.fillText('\\u2665', 256 * S, 256 * S);

  x.restore();
  return c.toDataURL('image/png');
}`;

(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext()).newPage();
  await p.setContent('<!doctype html><meta charset="utf-8"><body></body>');
  for (const [name, size, maskable] of FILES) {
    const data = await p.evaluate(
      ([src, s, m]) => (new Function('return ' + src))()(s, m), [DRAW, size, maskable]);
    const buf = Buffer.from(data.split(',')[1], 'base64');
    fs.writeFileSync(path.join(OUT, name), buf);
    console.log(`${name.padEnd(22)} ${size}x${size}${maskable ? ' maskable' : ''}  ${Math.round(buf.length / 1024)}KB`);
  }
  await b.close();

  /* say out loud whether anything is still missing */
  const want = ['sol-512.png', 'sol-192.png', 'sol-180.png', 'sol-maskable-512.png'];
  const gone = want.filter(f => !fs.existsSync(path.join(OUT, f)));
  console.log(gone.length ? 'STILL MISSING: ' + gone.join(', ') : 'every icon the page and the manifest ask for now exists');
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
