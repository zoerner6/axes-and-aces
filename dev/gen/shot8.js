const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 820 } }); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(3000); await p.screenshot({ path: 'u_story.png' });
  for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(300);} }
  await p.click('[data-act=fight]'); await p.waitForTimeout(500); await p.click('.skip').catch(()=>{}); await p.waitForTimeout(700); await p.screenshot({ path: 'u_fight.png' });
  await p.evaluate(()=>window.__T.trade()); await p.waitForTimeout(1900); await p.screenshot({ path: 'u_trade1.png' });
  await p.waitForTimeout(1300); await p.screenshot({ path: 'u_trade2.png' }); await p.waitForTimeout(2500); await p.screenshot({ path: 'u_trade3.png' });
  await p.evaluate(()=>window.__T.find()); await p.waitForTimeout(1500); await p.screenshot({ path: 'u_find.png' });
  await p.evaluate(()=>window.__T.vic()); await p.waitForTimeout(1500); await p.screenshot({ path: 'u_vic.png' });
  await p.evaluate(()=>window.__T.path()); await p.waitForTimeout(600); await p.screenshot({ path: 'u_path.png' });
  console.log(errs.join('|')||'no errors'); await b.close(); })();
