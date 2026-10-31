const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[]; const p = await b.newPage({ viewport: { width: 390, height: 820 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
  await p.click('[data-act=fight]'); await p.waitForTimeout(600);
  console.log(await p.evaluate(()=>window.__T.lv())); await p.waitForTimeout(300);
  await p.screenshot({ path: 'ace.png', clip:{x:0,y:520,width:390,height:160} });
  console.log(errs.join('|')||'no errors'); await b.close(); })();
