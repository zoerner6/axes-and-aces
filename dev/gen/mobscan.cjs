/* Phone screen sweep for the game.
   node dev/gen/mobscan.cjs [--sizes 390x844,360x740,320x568] [--only name] [--out dev/gen/out/ph]
   Opens audittest.html, drives it to each screen through window.__A.ev, runs
   dev/gen/audit.js and saves a screenshot per screen per size. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const args = process.argv.slice(2);
const flag = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const sizes = (flag('--sizes') || '390x844,360x740,320x568').split(',').map(s => s.split('x').map(Number));
const outDir = flag('--out') || 'dev/gen/out/ph';
const only = flag('--only');
const AUDIT = fs.readFileSync('dev/gen/audit.js', 'utf8');
const URL = 'http://localhost:8765/audittest.html';

const KIT = `S.idx=5; S.level=5; S.maxHp=800; S.hp=800;
  S.eq={main:{type:'axe',tier:3},off:null,shield:{type:'shield',tier:2},helm:{type:'helm',tier:3},armor:{type:'armor',tier:2}};
  S.huntFoe=null; S.foePick=null; S.genFoe=null;
  S.coach=-1; S.tips={shop:1,level:1,boss:1,path:1};`;

/* name, js to run, ms to wait, optional pre-step */
const SCREENS = [
  ['heroselect',  `slotsPanel()`, 3200],
  ['heroselect1', `localStorage.clear(); slotsPanel()`, 3200],
  ['story',       `S.phase='story'; S.story={key:'start',page:2}; storyPanel()`, 5500],
  ['enc-spot',    KIT + `S.enc='spot'; fightIntro()`, 6000],
  ['enc-path',    KIT + `S.enc='path'; fightIntro()`, 6000],
  ['enc-ambush',  KIT + `S.enc='ambush'; fightIntro()`, 6000],
  ['enc-boss',    KIT + `S.foePick='ghoul'; S.enc='boss'; fightIntro()`, 6000],
  ['fight',       KIT + `S.enc='spot'; fightIntro()`, 6000, 'fight'],
  ['shop-smith',  KIT + `S.gold=60; S.shopTab='smith'; shopPanel()`, 3000],
  ['shop-books',  KIT + `S.gold=60; S.shopTab='books'; shopPanel()`, 3000],
  ['shop-pots',   KIT + `S.gold=60; S.shopTab='pots'; shopPanel()`, 3000],
  ['path',        `S.idx=5; S.redo=true; S.huntFoe='gen'; S.huntArea=0; pathPanel()`, 3000],
  ['victory',     KIT + `S.enc='spot'; fightIntro()`, 6000, 'victory'],
  ['fallen',      `S.hp=0; S.killer={name:'Giant Spider',dmg:332,raw:420,saved:88,big:true,area:1}; gameOverPanel()`, 5000],
  ['levelup',     KIT + `S.pendingLv=1; levelPanel()`, 4500],
  ['guide',       `guidePanel()`, 2500],
  ['menu',        `menuPanel()`, 2500],
];

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const report = [];
  for (const [w, h] of sizes) {
    const tag = `${w}x${h}`;
    for (const [name, js, waitMs, extra] of SCREENS) {
      if (only && name !== only) continue;
      const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
      const p = await ctx.newPage();
      const errs = [];
      p.on('pageerror', e => errs.push(String(e.message).slice(0, 200)));
      p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
      try {
        await p.goto(URL, { waitUntil: 'load' });
        await p.waitForTimeout(1400);
        await p.evaluate(x => window.__A.ev(x), js);
        await p.waitForTimeout(waitMs);
        if (extra === 'fight' || extra === 'victory') {
          const btn = await p.$('[data-act=fight]');
          if (btn) { await btn.click(); await p.waitForTimeout(4500); }
        }
        if (extra === 'victory') {
          await p.evaluate(x => window.__A.ev(x), `busy=false; S.fight.hurt=false; S.hp=S.maxHp; victory();`);
          await p.waitForTimeout(7000);
        }
        await p.addScriptTag({ content: AUDIT });
        const r = await p.evaluate(l => window.__AUDIT(l), `${name}@${tag}`);
        await p.screenshot({ path: path.join(outDir, `${name}_${tag}.png`) });
        const doc = await p.evaluate(() => ({
          scrollH: document.documentElement.scrollHeight, innerH: innerHeight,
          panelScroll: (() => { const q = document.querySelector('#overlay:not([hidden]) .panel'); return q ? { sh: q.scrollHeight, ch: q.clientHeight } : null; })(),
        }));
        report.push({ screen: name, viewport: tag, ...r, doc, jsErrors: [...new Set(errs)] });
      } catch (e) {
        report.push({ screen: name, viewport: tag, FAILED: e.message, jsErrors: [...new Set(errs)] });
      }
      await ctx.close();
    }
  }
  await b.close();
  const slim = report.map(r => {
    const o = { screen: r.screen, vp: r.viewport };
    if (r.FAILED) { o.FAILED = r.FAILED; return o; }
    for (const k of ['overlaps', 'cropped', 'broken', 'clipped', 'offscreen', 'tiny', 'tapTargets'])
      if ((r[k] || []).length) o[k] = r[k];
    if (r.pageScrollsSideways) o.sideways = true;
    if (r.doc && r.doc.scrollH > r.doc.innerH + 2) o.pageScrollsDown = r.doc.scrollH + '>' + r.doc.innerH;
    if (r.doc && r.doc.panelScroll && r.doc.panelScroll.sh > r.doc.panelScroll.ch + 2) o.panelScrolls = r.doc.panelScroll.sh + '>' + r.doc.panelScroll.ch;
    if ((r.jsErrors || []).length) o.jsErrors = r.jsErrors;
    return o;
  });
  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(slim, null, 1));
  console.log(JSON.stringify(slim, null, 1));
})().catch(e => { console.error('RUNNER FAILED:', e.message); process.exit(1); });
