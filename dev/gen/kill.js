const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[]; const p = await b.newPage({ viewport: { width: 390, height: 820 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
  await p.click('[data-act=fight]'); await p.waitForTimeout(600);
  await p.evaluate(()=>window.__T.kill()); await p.waitForTimeout(300); await p.screenshot({ path: 'k1.png' });
  await p.waitForTimeout(900); await p.screenshot({ path: 'k2.png' });
  await p.waitForTimeout(2500); await p.screenshot({ path: 'k3.png' });
  await p.click('[data-act=afterVictory]'); await p.waitForTimeout(400); await p.click('[data-act=leaveShop]'); await p.waitForTimeout(1200); await p.screenshot({ path: 'k4.png' });
  console.log(errs.join('|')||'no errors'); await b.close(); })();
