const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  for (const [w,h] of [[390,860],[1100,860]]) { const p = await b.newPage({ viewport: { width: w, height: h } }); p.on('pageerror',e=>errs.push(e.message));
    await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true')}catch(e){} });
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(500);
    await p.evaluate(()=>window.__T.c()); await p.waitForTimeout(2200); await p.screenshot({ path: `l_${w}_c.png` });
    await p.evaluate(()=>window.__T.w()); await p.waitForTimeout(2200); await p.screenshot({ path: `l_${w}_w.png` });
    if(w===390){ await p.evaluate(()=>window.__T.fight()); await p.waitForTimeout(900); await p.screenshot({ path: `l_${w}_f.png` }); } }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
