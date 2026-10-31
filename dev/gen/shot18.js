const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  const ctx = await b.newContext({ viewport: { width: 390, height: 840 } }); const p = await ctx.newPage(); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(500);
  for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
  await p.click('[data-act=fight]'); await p.waitForTimeout(600);
  await p.evaluate(()=>window.__T.crit()); await p.waitForTimeout(400); await p.screenshot({ path: 'd_crit.png' });
  await p.click('[data-act=save]'); await p.waitForTimeout(300); await p.screenshot({ path: 'd_saved.png' });
  await p.reload(); await p.waitForTimeout(800); await p.screenshot({ path: 'd_title.png' });
  await p.click('[data-act=continue]'); await p.waitForTimeout(700); await p.screenshot({ path: 'd_cont.png' });
  await p.evaluate(()=>window.__T.die()); await p.waitForTimeout(3200); await p.screenshot({ path: 'd_die.png' });
  for (const w of [250,300,360]) { const q=await b.newPage({viewport:{width:w,height:700}}); await q.goto('http://localhost:8765/test.html'); await q.waitForTimeout(400);
    console.log(w, await q.evaluate(()=>document.documentElement.scrollWidth)); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
