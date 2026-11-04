/* Record the preview videos for the store listings.
     node dev/portal/farkle/trailer.cjs [poki|crazygames]

   Writes into store/portal-farkle/:
     preview-landscape-1920x1080.mp4
     preview-portrait-1080x1620.mp4

   Recorded off the real package while a bot actually plays it - rolls, sets
   dice aside, strikes, kills something - so the preview shows the game rather
   than a slideshow of screens.

   The game is laid out for a phone, so it is recorded at a phone size and
   then set on its own cover art for the two store shapes. That is better
   than recording at 1920 wide, where the game is a column in the middle of a
   lot of nothing.

   Needs ffmpeg on the PATH. */
/* a bot has played before: take the one-time walk-through offer out
   of the way, the same as a returning player */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');

const PORTAL = process.argv[2] || 'crazygames';
const ROOT = path.join(__dirname, '..', '..', '..');
const DIST = path.join(ROOT, 'dist', 'farkle-' + PORTAL);
const OUT = path.join(ROOT, 'store', 'portal-farkle');
const TMP = path.join(ROOT, 'dev', 'gen', 'out', 'fk', 'trailer');
const COVER = path.join(OUT, 'crazygames-cover-landscape-1920x1080.jpg');
if (!fs.existsSync(DIST)) { console.error('No package at ' + DIST); process.exit(2); }
if (!fs.existsSync(COVER)) { console.error('Run covers.cjs first: ' + COVER); process.exit(2); }

const W = 540, H = 960, SECONDS = 26;
const MIME = {'.html':'text/html','.js':'text/javascript','.webp':'image/webp','.png':'image/png',
  '.mp4':'video/mp4','.mp3':'audio/mpeg','.woff2':'font/woff2','.jpg':'image/jpeg','.css':'text/css'};

const tap = (pg, sel) => pg.evaluate(s => {
  const el = document.querySelector(s);
  if (!el || el.disabled) return false;
  el.click(); return true;
}, sel);

const ff = args => execFileSync('ffmpeg', ['-y', '-v', 'error', ...args], { stdio: 'inherit' });

(async () => {
  fs.rmSync(TMP, { recursive: true, force: true });
  fs.mkdirSync(TMP, { recursive: true });
  fs.mkdirSync(OUT, { recursive: true });

  const srv = http.createServer((q, r) => {
    const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
    const f = path.join(DIST, rel);
    if (!f.startsWith(DIST) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end('no'); }
    r.writeHead(200, { 'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(r);
  });
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/`;

  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await b.newContext({
    viewport: { width: W, height: H }, isMobile: true, hasTouch: true,
    recordVideo: { dir: TMP, size: { width: W, height: H } },
  });
  const p = await ctx.newPage();
  await p.goto(base, { waitUntil: 'load' });
  await p.evaluate(() => { try{ window.__FK.store.set('taught', true); }catch(e){} }).catch(() => {});
  await p.waitForTimeout(1800);
  /* the SDK's loading panel never clears on a local server; it is not part
     of the game and must not be the first thing a reviewer sees */
  await p.evaluate(() => {
    const mine = new Set(['app', 'overlay', 'fx']);
    for (const el of [...document.body.children]) {
      if (!mine.has(el.id) && !['SCRIPT', 'STYLE', 'LINK'].includes(el.tagName)) el.remove();
    }
  });

  /* Start part way in, so the preview opens on a real fight rather than on
     the first goblin in a tavern. */
  await p.evaluate(() => {
    const FK = window.__FK;
    FK.S.world = 2; FK.S.idx = 1; FK.S.level = 20;
    FK.S.hp = FK.S.maxHp; FK.S.introBeat = 9; FK.S.endBeat = 9;
    FK.closePanel(); FK.startFight();
  });
  await p.waitForTimeout(900);

  const t0 = Date.now();
  while (Date.now() - t0 < SECONDS * 1000) {
    const panel = await p.evaluate(() => {
      const o = document.getElementById('overlay');
      if (!o || o.hidden) return null;
      const btn = o.querySelector('[data-act="fight"], [data-act="onward"], [data-act="leaveShop"], '
        + '[data-act="storyNext"], [data-act="again"], [data-act="perk"], [data-act="close"]');
      if (btn) { btn.click(); return 'clicked'; }
      return 'stuck';
    });
    if (panel === 'stuck') break;
    if (panel === 'clicked') { await p.waitForTimeout(1500); continue; }   /* let the screen be seen */

    if (!await tap(p, '#rollBtn')) { await p.waitForTimeout(400); continue; }
    await p.waitForTimeout(820);
    for (let g = 0; g < 10; g++) {
      const st = await p.evaluate(() => {
        const FK = window.__FK, roll = FK.rollIdx();
        if (!roll.length) return { done: true };
        const best = FK.bestSplit(FK.facesOf(roll));
        if (!best.score) return { done: true };
        best.keep.forEach(k => {
          const el = document.querySelector(`[data-die="${roll[k]}"]`);
          if (el && !el.disabled) el.click();
        });
        return { wind: +document.getElementById('windNum').textContent.replace(/,/g, ''),
                 roll: !document.getElementById('rollBtn').disabled,
                 strike: !document.getElementById('strikeBtn').disabled };
      });
      if (st.done) break;
      await p.waitForTimeout(520);
      if (st.wind >= 550 || !st.roll) {
        if (st.strike) { await tap(p, '#strikeBtn'); await p.waitForTimeout(1500); }
        break;
      }
      await tap(p, '#rollBtn');
      await p.waitForTimeout(820);
    }
  }

  const video = p.video();
  await ctx.close();
  const raw = await video.path();
  await b.close(); srv.close();

  /* The phone recording, set on the game's own cover art for each shape.
     scale keeps the aspect; the cover is blurred and darkened so the game is
     plainly the subject and the backdrop is plainly a backdrop. */
  const land = path.join(OUT, 'preview-landscape-1920x1080.mp4');
  ff(['-i', raw, '-loop', '1', '-i', COVER,
      '-filter_complex',
      '[1:v]scale=1920:1080,boxblur=18:2,eq=brightness=-0.16[bg];'
      + '[0:v]scale=-2:1004,pad=iw+12:ih+12:6:6:color=0x000000[game];'
      + '[bg][game]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[v]',
      '-map', '[v]', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium',
      '-movflags', '+faststart', '-r', '30', land]);

  const port = path.join(OUT, 'preview-portrait-1080x1620.mp4');
  ff(['-i', raw, '-loop', '1', '-i', COVER,
      '-filter_complex',
      '[1:v]scale=1080:1620:force_original_aspect_ratio=increase,crop=1080:1620,'
      + 'boxblur=18:2,eq=brightness=-0.16[bg];'
      + '[0:v]scale=-2:1560,pad=iw+12:ih+12:6:6:color=0x000000[game];'
      + '[bg][game]overlay=(W-w)/2:(H-h)/2:shortest=1,format=yuv420p[v]',
      '-map', '[v]', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium',
      '-movflags', '+faststart', '-r', '30', port]);

  for (const f of [land, port]) {
    const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0',
      '-show_entries', 'stream=width,height,duration', '-of', 'json', f]).toString());
    const s = probe.streams[0];
    const mb = fs.statSync(f).size / 2 ** 20;
    const want = f === land ? [1920, 1080] : [1080, 1620];
    const right = s.width === want[0] && s.height === want[1];
    const longEnough = (+s.duration || 0) >= 10;
    console.log(`${right && longEnough ? '  ok  ' : 'CHECK '}${path.basename(f).padEnd(38)}`
      + `${s.width}x${s.height}  ${(+s.duration || 0).toFixed(1)}s  ${mb.toFixed(1)}MB`);
    if (!right) console.log(`        wanted ${want[0]}x${want[1]}`);
    if (!longEnough) console.log('        too short to show anything');
  }
  fs.rmSync(TMP, { recursive: true, force: true });
})();
