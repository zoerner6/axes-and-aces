const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  const p = await b.newPage({ viewport: { width: 390, height: 820 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
  await p.click('[data-act=fight]'); await p.waitForTimeout(600);
  await p.screenshot({ path: 'q_fight0.png' });
  await p.click('#hand .card:nth-child(1)'); await p.waitForTimeout(150); await p.screenshot({ path: 'q_fight1.png' });
  await p.click('#discBtn'); await p.waitForTimeout(1500); await p.screenshot({ path: 'q_fight2.png' });
  await p.evaluate(()=>window.__T.shop()); await p.waitForTimeout(600);
  await p.evaluate(()=>{const q=document.getElementById('panel'); q.style.maxHeight='none';}); await p.setViewportSize({width:390,height:2000}); await p.waitForTimeout(300);
  await p.screenshot({ path: 'q_shop.png' });
  console.log(errs.join('|')||'no errors'); await b.close(); })();
