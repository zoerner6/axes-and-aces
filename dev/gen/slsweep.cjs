/* The phone sweep: every screen in Monster Solitaire, at every size that
   matters, measured and photographed.

   node dev/gen/slsweep.cjs [--out dir] [--sizes 320x568,390x844]

   dev/gen/slscan.cjs checks the board and dev/gen/slpanels.cjs checks the
   popups. This drives the whole game - board states and popups together -
   runs dev/gen/audit.js on each, and writes a picture per screen per size, so
   the screenshots can be looked at one by one rather than only the report.

   Served over http rather than opened off disk, because a brag card cannot be
   drawn from a file:// page: the canvas is tainted and toDataURL throws. */
const { chromium } = require('playwright');
const { openGame } = require('./slopen.cjs');
const { execFileSync } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const args = process.argv.slice(2);
const flag = (n, d) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : d; };
const OUT = path.resolve(flag('--out', path.join(ROOT, 'dev', 'gen', 'out', 'sweep')));
const SIZES = flag('--sizes', '320x568,360x740,375x667,390x844').split(',').map(s => s.split('x').map(Number));

execFileSync('python', ['dev/build.py'], { cwd: ROOT, stdio: 'pipe' });
fs.mkdirSync(OUT, { recursive: true });

const TYPES = { '.html':'text/html', '.webp':'image/webp', '.png':'image/png', '.jpg':'image/jpeg',
                '.mp3':'audio/mpeg', '.mp4':'video/mp4', '.json':'application/json',
                '.js':'text/javascript', '.css':'text/css', '.webmanifest':'application/manifest+json' };
function serve(root){
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const rel = decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html';
      /* the leaderboard and the save code are server-side on the real site;
         here they are answered flatly, so a sweep is never red for the one
         thing a static file server cannot do */
      if (rel.startsWith('.netlify/functions/')) {
        res.writeHead(200, { 'content-type': 'application/json' });
        return res.end('{"scores":[],"ok":true}');
      }
      const f = path.join(root, rel);
      if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end('no'); }
      res.writeHead(200, { 'content-type': TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve({ srv, port: srv.address().port }));
  });
}

/* Every screen, as a thing to do in the page. Board screens leave the overlay
   shut; popup screens open one. */
/* Every screen starts from the same plausible hero. Without this they ran in
   order and leaked state into each other, which is how a victory screen came
   to show "GOLD -6" and a level-up "700 -> 400": the panels are called
   directly, without the bookkeeping the real path does before them, on top of
   whatever the screen before had left behind. */
const RESET = `
  S = SOL.freshHero();
  S.level = 6; S.maxHp = 400 + 100 * 5; S.hp = Math.round(S.maxHp * .55);
  S.gold = 64; S.xp = SOL.cumNeed(5) + 30;
  S.eq = { main:{type:'sword',tier:2}, armor:{type:'armor',tier:1} };
  SOL.S = S;
  SOL.coachLearned = ['play','stock','run','clear'];
  SOL.startFight(); SOL.closePanel();
`;

const SCREENS = [
  ['heroes',      `S.name='Edward'; S.level=6; SOL.saveGame(); SOL.slotsPanel();`],
  ['story-start', `S.world=0; S.introBeat=0; SOL.storyPanel('start');`],
  ['story-area',  `S.world=0; SOL.storyPanel('a2');`],
  ['story-end',   `S.world=1; S.endBeat=0; SOL.storyPanel('end');`],
  ['intro-ambush',`SOL.fightIntro('ambush');`],
  ['intro-spot',  `SOL.fightIntro('spot');`],
  ['intro-path',  `SOL.fightIntro('path');`],
  ['intro-boss',  `S.step=2; SOL.startFight(); SOL.closePanel(); SOL.fightIntro('boss');`],
  ['board',       ``],
  ['board-run',   `SOL.R.run=7; SOL.R.runVal=58; SOL.render();`],
  ['board-stuck', `SOL.R.tableau.forEach(c=>{if(!c.gone)c.r=7}); SOL.R.waste=[{r:2,s:0}]; SOL.R.si=SOL.R.stock.length; SOL.render();`],
  ['board-peak',  `SOL.R=SOL.dealRound(); SOL.LAYOUT.peak.forEach((k,i)=>{if(k===0)SOL.R.tableau[i].gone=true}); SOL.R.down=[0]; SOL.render();`],
  ['board-pouch', `SOL.R=SOL.dealRound(); S.pots=['heal','iron','rage']; S.ironskin=true; S.rage=true; SOL.render(); SOL.renderPots();`],
  /* the gold and the experience are added before the panel on the real
     path, so they are added here too rather than counting up from behind */
  ['victory',     `S.gold+=S.fight.gold; S.xp+=S.fight.xp; SOL.victoryPanel(S.fight,{flawless:false,clean:false,clutch:false,bonus:0});`],
  ['victory-mark',`const bn=S.fight.gold; S.gold+=S.fight.gold+bn; S.xp+=S.fight.xp;
                   SOL.victoryPanel(S.fight,{flawless:true,clean:false,clutch:false,bonus:bn});`],
  /* level up the way the game does it, not by setting the number: levelPanel
     compares against the health of the level below, so forcing S.level on its
     own drew "700 -> 400" and made it look as if levelling cost you health */
  ['level',       `SOL.levelUp(); SOL.levelPanel();`],
  /* underlevelled on purpose, so the warning is on screen - and with the
     health that goes with being level 1, or the picture says level 1 beside
     900 health and reads as a bug */
  ['crossing',    `S.level=1; S.maxHp=400; S.hp=220; S.step=2; S.area=0; SOL.pathPanel();`],
  ['shop-rest',   `S.charms=['cup']; S.pots=['heal']; SOL.shopPanel('rest');`],
  ['shop-smith',  `SOL.shopPanel('smith');`],
  ['shop-charms', `SOL.shopPanel('charms');`],
  ['shop-pots',   `SOL.shopPanel('pots');`],
  ['fallen',      `SOL.lost();`],
  ['menu',        `SOL.menuPanel();`],
  ['help-1',      `SOL.helpPanel(0);`],
  ['help-2',      `SOL.helpPanel(1);`],
  ['leaderboard', `SOL.lbPanel();`],
  ['cloud',       `SOL.cloudPanel();`],
  ['daily-intro', `SOL.startDaily();`],
  ['brag',        `S.bestRun=11; S.wins=14; S.lastWin={name:'Bandit Chief',slug:'bandit',boss:true}; SOL.bragPanel('run');`],
];

const PLAIN = s => String(s).replace(/\s+/g, ' ').trim();

(async () => {
  const { srv, port } = await serve(ROOT);
  const url = `http://127.0.0.1:${port}/solitaire.html`;
  const audit = fs.readFileSync(path.join(ROOT, 'dev/gen/audit.js'), 'utf8');
  const b = await chromium.launch();
  let bad = 0, shots = 0;

  for (const [w, h] of SIZES) {
    console.log(`\n${w}x${h}`);
    const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2,
      isMobile: w <= 560, hasTouch: w <= 560 });
    const p = await ctx.newPage();
    await p.route('**/vid/**', r => r.abort());
    await p.route('**/music/**', r => r.abort());
    await p.route(/\.netlify\/functions\//   /* a glob stops at the ?, and these all carry a query */, r =>
      r.fulfill({ status: 200, contentType: 'application/json', body: '{"scores":[]}' }));
    const errs = [];
    /* "404 (Not Found)" on its own tells you nothing; the URL tells you
       everything, and a file the page asks for on every load and never gets
       is worth naming. */
    const missing = new Set();
    p.on('response', r => { if (r.status() === 404) missing.add(r.url().replace(url.replace(/\/solitaire\.html$/, '/'), '')); });
    p.on('pageerror', e => errs.push(PLAIN(e.message).slice(0, 150)));
    p.on('console', m => { if (m.type() === 'error' && !/vid\/|music\/|ERR_|404 \(Not Found\)/.test(m.text())) errs.push(PLAIN(m.text()).slice(0, 150)); });
    await p.goto(url, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);
    await openGame(p);
    await p.addScriptTag({ content: audit });

    for (const [name, code] of SCREENS) {
      try {
        await p.evaluate(([reset, src]) => {
          const SOL = window.__SOL;
          let S = SOL.S;
          eval(reset);            // eslint-disable-line no-eval
          S = SOL.S;
          eval(src);              // eslint-disable-line no-eval
        }, [RESET, code]);
      } catch (e) { console.log(`  ${name.padEnd(13)} *** would not open: ${PLAIN(e.message).slice(0, 70)}`); bad++; continue; }
      /* Most of these screens are popups, and some of them take their time:
         the fallen screen banners for a second and a half before it opens.
         Waiting a flat moment photographed the banner instead of the panel,
         so the one screen that most needed looking at was never in the set. */
      const isBoard = name.startsWith('board');
      await p.waitForTimeout(name.startsWith('brag') ? 1400 : 300);
      if (!isBoard) {
        await p.waitForFunction(() => !document.getElementById('overlay').hidden,
          null, { timeout: 6000 }).catch(() => {});
      }
      await p.waitForTimeout(260);
      /* A typed line arrives over seconds, and a panel measured half-typed is
         a shorter panel than a player ever sees. Wait for the words to stop
         arriving rather than for a fixed moment. */
      await p.waitForFunction(() => {
        const t = ['#storyText', '#encSay', '#encCap']
          .map(s => (document.querySelector(s) || {}).textContent || '').join('').length;
        const was = window.__typedWas;
        window.__typedWas = t;
        return was === t;
      }, null, { timeout: 9000 }).catch(() => {});
      await p.evaluate(() => { window.__typedWas = -1; });

      const m = await p.evaluate(() => {
        const PLAIN = s => String(s).replace(/\s+/g, ' ').trim();
        const panel = document.querySelector('#overlay').hidden ? null : document.querySelector('#panel');
        const rows = panel ? [...panel.querySelectorAll('.btn.big, .perk, .buy[data-act]')] : [];
        const main = panel ? (panel.querySelector('.btn.big') || rows[rows.length - 1]) : null;
        const mr = main ? main.getBoundingClientRect() : null;
        const taps = [...document.querySelectorAll('.tool, .pk.free, [data-act="turn"], .pot, .btn, .buy, .perk, .tab')]
          .filter(e => { const r = e.getBoundingClientRect(); return r.width > 1 && r.height > 1; })
          .map(e => ({ what: e.dataset.act || PLAIN(e.textContent).slice(0, 12) || e.className,
                       min: Math.round(Math.min(e.getBoundingClientRect().width, e.getBoundingClientRect().height)) }));
        return {
          panel: !!panel,
          scrolls: panel ? panel.scrollHeight > panel.clientHeight + 1 : false,
          mainBottom: mr ? Math.round(mr.bottom) : null,
          mainIn: mr ? mr.bottom <= innerHeight + 1 : true,
          sideways: document.documentElement.scrollWidth > innerWidth + 1,
          smallTaps: taps.filter(t => t.min < 44),
          audit: window.__AUDIT(name)
        };
      });

      const a = m.audit, notes = [];
      if (m.scrolls) { notes.push('the panel needs scrolling'); bad++; }
      if (!m.mainIn) { notes.push(`its main control is ${m.mainBottom - h}px below the screen`); bad++; }
      if (m.sideways) { notes.push('scrolls sideways'); bad++; }
      if (m.smallTaps.length) { notes.push('under 44px: ' + m.smallTaps.map(t => `${t.what} ${t.min}`).join(', ')); bad++; }
      if (a.overlaps.length) { notes.push('text on text: ' + a.overlaps.map(o => `"${o.a}" x "${o.b}"`).join(' | ')); bad++; }
      if (a.cropped.length) { notes.push('art sliced: ' + a.cropped.map(c => `${c.src} sides ${c.cutSides} ends ${c.cutTopBottom}`).join(' | ')); bad++; }
      if (a.broken.length) { notes.push('missing art: ' + a.broken.join(', ')); bad++; }
      if (a.clipped && a.clipped.length) { notes.push('clipped: ' + a.clipped.map(c => PLAIN(c.text || c)).slice(0, 3).join(' | ')); bad++; }
      if (a.tiny && a.tiny.length) { notes.push('under 10.5px: ' + a.tiny.map(t => PLAIN(t.text || t)).slice(0, 3).join(' | ')); bad++; }

      const file = path.join(OUT, `${w}x${h}_${name}.png`);
      await p.screenshot({ path: file });
      shots++;
      console.log(`  ${name.padEnd(13)} ${notes.length ? '' : 'clean'}`);
      notes.forEach(n => console.log('      ** ' + n));
    }
    if (missing.size) { console.log('      ** asked for and not there: ' + [...missing].join(', ')); bad++; }
    if (errs.length) { console.log('      ** JS: ' + [...new Set(errs)].join(' | ')); bad++; }
    await ctx.close();
  }

  await b.close();
  srv.close();
  console.log(`\n${shots} screenshots in ${OUT}`);
  console.log(bad ? `${bad} problems` : 'the sweep is clean');
  if (bad) process.exit(1);
})().catch(e => { console.error('FAILED:', e.message); process.exit(1); });
