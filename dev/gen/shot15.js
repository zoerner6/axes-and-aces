const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  for (const [w,h] of [[390,820],[1100,800]]) { const p = await b.newPage({ viewport: { width: w, height: h } }); p.on('pageerror',e=>errs.push(e.message));
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(500);
    await p.evaluate(()=>{ document.getElementById('overlay').hidden=true; window.__T.fin(); }); await p.waitForTimeout(4400); await p.screenshot({ path: `ff_${w}.png` });
    await p.waitForTimeout(1800); await p.evaluate(()=>window.__T.shop()); await p.waitForTimeout(500); await p.screenshot({ path: `fs_${w}.png` }); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
