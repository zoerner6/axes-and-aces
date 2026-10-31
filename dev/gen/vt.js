const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  for (const [w,h] of [[390,820],[1100,800]]) { const p = await b.newPage({ viewport: { width: w, height: h } }); p.on('pageerror',e=>errs.push(e.message));
    await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
    for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
    await p.click('[data-act=fight]'); await p.waitForTimeout(1500);
    console.log(w, await p.evaluate(()=>window.__T.st())); await p.screenshot({ path: `v1_${w}.png` });
    await p.evaluate(()=>window.__T.atk()); await p.waitForTimeout(1600); await p.screenshot({ path: `v2_${w}.png` });
    await p.waitForTimeout(3000); await p.evaluate(()=>window.__T.kill()); await p.waitForTimeout(1300); await p.screenshot({ path: `v3_${w}.png` }); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
