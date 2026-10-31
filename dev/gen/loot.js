const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  const p = await b.newPage({ viewport: { width: 390, height: 860 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  console.log(await p.evaluate(()=>window.__T.stats()));
  await p.evaluate(()=>window.__T.vg()); await p.waitForTimeout(2200); await p.screenshot({ path: 'lt_gear.png' });
  await p.evaluate(()=>window.__T.vp()); await p.waitForTimeout(2200); await p.screenshot({ path: 'lt_pot.png' });
  console.log(errs.join('|')||'no errors'); await b.close(); })();
