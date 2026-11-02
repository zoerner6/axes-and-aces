/* Phone screen sweep for Monster Farkle.
     node dev/gen/fkscan.cjs [--sizes 390x844,375x667,360x740,320x568]
                             [--only name] [--out dev/gen/out/fk] [--probe]
   Builds farkletest.html with dev/gen/harness.py, serves the repo, drives the
   game to each screen through window.__A.ev, runs dev/gen/audit.js and saves a
   screenshot per screen per size.

   --probe just answers the one question that has to be true before any phone
   measurement is worth anything: is the phone CSS actually live? The source has
   no <head>, so a page built by hand has no viewport meta, and Chrome then lays
   it out at 980px while every max-width query silently reads false. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);

const args = process.argv.slice(2);
const flag = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const has = n => args.includes(n);
const sizes = (flag('--sizes') || '390x844,375x667,360x740,320x568').split(',').map(s => s.split('x').map(Number));
const outDir = flag('--out') || 'dev/gen/out/fk';
const only = flag('--only');

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.mp4': 'video/mp4', '.mp3': 'audio/mpeg' };

/* name, js to run, ms to wait. KIT gives the hero enough to show every part
   of the screen at once: gear, charms, potions and a level waiting. */
const KIT = `S.level=5; S.maxHp=800; S.hp=620; S.gold=48; S.xp=cumNeed(4)+10;
  S.eq={main:{type:'axe',tier:3},off:null,shield:{type:'shield',tier:2},helm:{type:'helm',tier:3},armor:{type:'armor',tier:2}};
  S.charms=['whet','cup']; S.pots=['heal','iron','rage'];`;
const SCREENS = [
  ['heroes',      `localStorage.clear(); slotsPanel()`, 1200],
  ['story-start', `closePanel(); S.introBeat=0; storyPanel('start')`, 2600],
  ['story-area',  `closePanel(); S.world=0; S.idx=3; storyPanel('a1')`, 2600],
  ['enc-normal',  KIT + `closePanel(); S.world=0; S.idx=1; startFight()`, 3000],
  ['enc-boss',    KIT + `closePanel(); S.world=0; S.idx=2; startFight()`, 3000],
  ['fight',       KIT + `closePanel(); S.world=0; S.idx=1; startFight(); setTimeout(()=>{closePanel();busy=false;renderDice();},1200)`, 3200],
  ['fight-mid',   KIT + `closePanel(); S.world=0; S.idx=1; startFight(); setTimeout(()=>{closePanel();busy=false;started=true;window.__FK.setFaces([1,5,3,3,6,2]);document.querySelector('[data-die="0"]').click();document.querySelector('[data-die="1"]').click();},1200)`, 3200],
  ['fight-boss',  KIT + `closePanel(); S.world=4; S.idx=2; startFight(); setTimeout(()=>{closePanel();busy=false;renderDice();},1200)`, 3400],
  ['farkle',      KIT + `closePanel(); S.world=0; S.idx=1; startFight(); setTimeout(()=>{closePanel();busy=false;started=true;window.__FK.setFaces([2,3,4,6,2,3]);wind=900;renderWind();farkle();},1200)`, 3000],
  ['strike',      KIT + `closePanel(); S.world=0; S.idx=1; startFight(); setTimeout(()=>{closePanel();busy=false;started=true;window.__FK.setFaces([1,1,1,1,1,1]);[0,1,2,3,4,5].forEach(i=>document.querySelector('[data-die="'+i+'"]').click());setTimeout(()=>doStrike(),300);},1200)`, 3300],
  ['victory',     KIT + `closePanel(); S.world=0; S.idx=1; startFight(); setTimeout(()=>{closePanel();busy=false;S.tookHit=false;S.fight.hp=0;won();},1200)`, 4200],
  ['levelup',     KIT + `closePanel(); S.pendingLv=1; S.level=5; levelPanel()`, 1400],
  ['shop-rest',   KIT + `closePanel(); shopPanel('rest')`, 1100],
  ['shop-smith',  KIT + `closePanel(); shopPanel('smith')`, 1100],
  ['shop-charms', KIT + `closePanel(); shopPanel('charms')`, 1100],
  ['shop-pots',   KIT + `closePanel(); shopPanel('pots')`, 1100],
  ['fallen',      KIT + `closePanel(); S.world=0; S.idx=1; startFight(); setTimeout(()=>{closePanel();busy=false;S.hp=0;lost();},1200)`, 3400],
  ['guide',       `closePanel(); guidePanel()`, 1000],
  ['help',        `closePanel(); helpPanel()`, 1000],
  ['menu',        `closePanel(); menuPanel()`, 1000],
  ['cloud',       `closePanel(); cloudPanel()`, 1000],
  ['hall',        `closePanel(); lbPanel()`, 1800],
  ['daily',       `closePanel(); startDaily()`, 1200],
  ['daily-done',  `closePanel(); startDaily(); S.daily.score=14820; S.wins=4; dailyDone()`, 1600],
  ['brag',        KIT + `closePanel(); S.bestHit=4820; S.lastWin={name:'Bandit Chief',slug:'bandit',boss:true}; bragPanel('boss')`, 3200],
];

function serve() {
  const srv = http.createServer((req, res) => {
    const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'farkletest.html';
    const file = path.join(ROOT, rel);
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404); return res.end('no');
    }
    res.writeHead(200, { 'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(r => srv.listen(0, '127.0.0.1', () => r(srv)));
}

(async () => {
  execFileSync('python', ['dev/gen/harness.py', 'dev/farkle.html', 'farkletest.html'], { stdio: 'inherit' });
  const srv = await serve();
  const base = `http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});

  if (has('--probe')) {
    for (const [w, h] of sizes) {
      const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
      const p = await ctx.newPage();
      await p.goto(base, { waitUntil: 'load' });
      const r = await p.evaluate(() => ({
        layoutWidth: document.documentElement.clientWidth,
        phone560: matchMedia('(max-width:560px)').matches,
        phone400: matchMedia('(max-width:400px)').matches,
        phone380: matchMedia('(max-width:380px)').matches,
        hook: typeof window.__A === 'object',
        sideScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      }));
      const ok = r.layoutWidth === w && r.phone560;
      console.log(`${w}x${h}  layout=${r.layoutWidth}  (max-width:560px)=${r.phone560}  400=${r.phone400}  380=${r.phone380}  sideScroll=${r.sideScroll}  hook=${r.hook}  ${ok ? 'OK' : 'BROKEN'}`);
      await ctx.close();
      if (!ok) { await b.close(); srv.close(); process.exit(1); }
    }
    await b.close(); srv.close();
    console.log('\nPhone CSS is live at every size. Measurements can be trusted.');
    return;
  }

  const AUDIT = fs.readFileSync('dev/gen/audit.js', 'utf8');
  fs.mkdirSync(outDir, { recursive: true });
  const report = [];
  for (const [w, h] of sizes) {
    const tag = `${w}x${h}`;
    for (const [name, js, waitMs] of SCREENS) {
      if (only && name !== only) continue;
      const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
      const p = await ctx.newPage();
      const errs = [];
      p.on('pageerror', e => errs.push(String(e.message).slice(0, 200)));
      p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
      try {
        await p.goto(base, { waitUntil: 'load' });
        await p.waitForTimeout(700);
        if (!await p.evaluate(() => matchMedia('(max-width:560px)').matches))
          throw new Error('phone CSS is NOT live - the viewport meta is missing');
        if (js) await p.evaluate(x => window.__A.ev(x), js);
        await p.waitForTimeout(waitMs);
        await p.addScriptTag({ content: AUDIT });
        const r = await p.evaluate(l => window.__AUDIT(l), `${name}@${tag}`);
        await p.screenshot({ path: path.join(outDir, `${name}_${tag}.png`) });
        /* no popup may need scrolling to reach its main button */
        const over = await p.evaluate(() => {
          const ov = document.getElementById('overlay');
          if(!ov || ov.hidden) return null;
          const el = document.getElementById('panel');
          const spill = el.scrollHeight - el.clientHeight;
          if(spill <= 1) return null;
          const big = [...el.children].filter(c => c.classList.contains('btn') && c.classList.contains('big'));
          const last = big[big.length - 1];
          return { spill, mainButtonBelowTheFold: last ? Math.round(last.getBoundingClientRect().bottom - el.getBoundingClientRect().bottom) : null };
        });
        if(over) r.panelScrolls = [over];
        r.errors = errs;
        report.push(r);
      } catch (e) {
        report.push({ label: `${name}@${tag}`, fatal: String(e.message).slice(0, 300), errors: errs });
      }
      await ctx.close();
    }
  }
  await b.close(); srv.close();

  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(report, null, 1));
  let bad = 0;
  for (const r of report) {
    const bits = [];
    if (r.fatal) bits.push('FATAL ' + r.fatal);
    for (const k of ['overlaps', 'cropped', 'broken', 'clipped', 'offscreen', 'tiny', 'tapTargets', 'panelScrolls'])
      if (r[k] && r[k].length) bits.push(`${k}=${r[k].length}`);
    if (r.errors && r.errors.length) bits.push(`jsErrors=${r.errors.length}`);
    if (bits.length) { bad++; console.log(`${r.label}  ${bits.join('  ')}`); }
  }
  console.log(bad ? `\n${bad} of ${report.length} screens have findings. See ${outDir}/report.json` : `\nAll ${report.length} screens clean.`);
})();
