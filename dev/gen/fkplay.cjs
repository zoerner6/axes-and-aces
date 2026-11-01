/* Play Monster Farkle through, by tapping, and report what happened.
   Catches the things a screenshot cannot: a loop that stalls, a button left
   disabled forever, health that goes the wrong way, a turn that never ends.
     node dev/gen/fkplay.cjs [turns] */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
process.chdir(ROOT);
const MIME = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.webp':'image/webp',
  '.png':'image/png','.mp4':'video/mp4','.mp3':'audio/mpeg','.json':'application/json','.jpg':'image/jpeg'};
execFileSync('python', ['dev/gen/harness.py','dev/farkle.html','farkletest.html'], {stdio:'inherit'});
const srv = http.createServer((q,r)=>{
  const rel = decodeURIComponent(q.url.split('?')[0]).replace(/^\/+/,'') || 'farkletest.html';
  const f = path.join(ROOT, rel);
  if(!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ r.writeHead(404); return r.end('no'); }
  r.writeHead(200, {'content-type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream'});
  fs.createReadStream(f).pipe(r);
});
const TURNS = +(process.argv[2] || 14);
(async () => {
  await new Promise(z => srv.listen(0, '127.0.0.1', z));
  const base = `http://127.0.0.1:${srv.address().port}/farkletest.html`;
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const ctx = await b.newContext({viewport:{width:390,height:844}, deviceScaleFactor:1,
    isMobile:true, hasTouch:true, reducedMotion:'reduce'});
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('PAGE: ' + e.message));
  p.on('console', m => { if(m.type()==='error') errs.push('CONSOLE: ' + m.text().slice(0,160)); });
  await p.goto(base, {waitUntil:'load'});
  await p.waitForTimeout(700);

  const look = () => p.evaluate(() => ({
    foe: document.getElementById('foeName').textContent,
    foeHp: Math.round(parseFloat(document.getElementById('foeBar').style.height||'100')),
    hp: window.__FK.S.hp, maxHp: window.__FK.S.maxHp,
    lv: window.__FK.S.level, gold: window.__FK.S.gold, xp: window.__FK.S.xp,
    gear: Object.keys(window.__FK.S.eq).filter(k=>window.__FK.S.eq[k]).length,
    charms: (window.__FK.S.charms||[]).length, pots: (window.__FK.S.pots||[]).length,
    wind: document.getElementById('windNum').textContent,
    roll: document.getElementById('rollBtn').disabled,
    strike: document.getElementById('strikeBtn').disabled,
    note: document.getElementById('windNote').textContent,
    banner: document.getElementById('banner').textContent,
    wins: window.__FK.S.wins, deaths: window.__FK.S.deaths,
  }));
  /* wait for the game to be ready for input again */
  async function settle(ms = 20000){
    const t0 = Date.now();
    for(;;){
      /* the timeout check belongs at the TOP: every branch below continues the
         loop, so a check at the bottom is never reached once one of them hits */
      if(Date.now() - t0 > ms){
        console.log('  settle gave up. Overlay up?',
          await p.evaluate(() => !document.getElementById('overlay').hidden),
          'buttons:', await p.evaluate(() => [...document.querySelectorAll('#overlay [data-act]')].map(b=>b.dataset.act).join(',')));
        return false;
      }
      /* clear whatever popup is up: Fight!, Onward, a perk, Try again */
      /* At the merchant: rest if hurt, buy the first thing affordable, else
         leave. All of it inside one evaluate, because clicking a tab
         re-renders the panel and any node held from before is then detached -
         clicking it does nothing and the loop spins forever. */
      const atShop = await p.evaluate(() => {
        if(!document.querySelector('[data-act="leaveShop"]')) return null;
        const S = window.__FK.S;
        if(S.hp < S.maxHp * .7){
          const r = document.querySelector('[data-act="rest"]:not([disabled])');
          if(r){ r.click(); return 'rest'; }
        }
        for(const tab of ['smith','charms','pots']){
          const t = document.querySelector(`[data-act="shopTab"][data-tab="${tab}"]`);
          if(t) t.click();
          const buy = document.querySelector('[data-act="buyEq"]:not([disabled]), [data-act="buyCharm"]:not([disabled]), [data-act="buyPot"]:not([disabled])');
          if(buy){ buy.click(); return 'bought ' + tab; }
        }
        document.querySelector('[data-act="leaveShop"]').click();
        return 'left';
      });
      if(atShop){ await p.waitForTimeout(300); continue; }
      const btn = await p.$('#overlay:not([hidden]) [data-act="fight"], #overlay:not([hidden]) [data-act="onward"], #overlay:not([hidden]) [data-act="perk"], #overlay:not([hidden]) [data-act="again"]');
      if(btn){ await btn.click().catch(()=>{}); await p.waitForTimeout(350); continue; }
      const r = await p.evaluate(() => !document.getElementById('rollBtn').disabled);
      if(r) return true;
      await p.waitForTimeout(120);
    }
  }

  let stalls = 0, strikes = 0, farkles = 0, wins = 0, losses = 0;
  for(let t = 1; t <= TURNS; t++){
    if(!await settle()){ console.log(`turn ${t}: STALLED - Roll never came back`); stalls++; break; }
    const before = await look();
    await p.click('#rollBtn');
    await p.waitForTimeout(500);
    /* set aside the best split the game itself would pick, then decide */
    let guard = 0;
    for(;;){
      if(guard++ > 12){ console.log('  guard trip'); break; }
      const picked = await p.evaluate(() => {
        const FK = window.__FK;
        const roll = FK.rollIdx();
        if(!roll.length) return 'none';
        const faces = FK.facesOf(roll);
        const best = FK.bestSplit(faces);
        if(!best.score) return 'farkle';
        best.keep.forEach(k => {
          const el = document.querySelector(`[data-die="${roll[k]}"]`);
          if(el && !el.disabled) el.click();
        });
        return best.score;
      });
      if(picked === 'farkle' || picked === 'none') break;
      await p.waitForTimeout(160);
      const st = await p.evaluate(() => ({
        wind: +document.getElementById('windNum').textContent.replace(/,/g,''),
        roll: !document.getElementById('rollBtn').disabled,
        strike: !document.getElementById('strikeBtn').disabled }));
      if(st.wind >= 300 || !st.roll){
        if(st.strike){ await p.click('#strikeBtn'); strikes++; }
        break;
      }
      await p.click('#rollBtn');
      await p.waitForTimeout(800);
      const far = await p.evaluate(() => document.getElementById('windNote').textContent.indexOf('Farkle') >= 0);
      if(far){ farkles++; break; }
    }
    await p.waitForTimeout(900);
    const after = await look();
    wins = after.wins; losses = after.deaths;
    console.log(`turn ${String(t).padStart(2)}  ${before.foe.padEnd(16)} Lv${before.lv} foeHp ${String(before.foeHp).padStart(3)}% -> ${String(after.foeHp).padStart(3)}%   you ${String(after.hp).padStart(4)}/${after.maxHp}  g${after.gold} xp${after.xp} gear${after.gear} ch${after.charms} p${after.pots}  W${after.wins}/D${after.deaths}  ${after.banner ? '[' + after.banner.slice(0,30) + ']' : ''}`);
    if(after.hp < 0) console.log('  BUG: health went below zero');
    if(after.foeHp < 0) console.log('  BUG: monster health went below zero');
  }
  console.log(`\nstrikes ${strikes}  farkles ${farkles}  wins ${wins}  losses ${losses}  stalls ${stalls}`);
  console.log('js errors:', errs.length ? errs.slice(0,6) : 'none');
  await b.close(); srv.close();
  process.exit(stalls || errs.length ? 1 : 0);
})();
