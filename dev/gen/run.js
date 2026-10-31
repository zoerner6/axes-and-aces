const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[]; const p = await b.newPage({ viewport: { width: 390, height: 820 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  for(let i=0;i<3;i++){ const el=await p.$('[data-act=storyNext]'); if(el){ await el.click(); await p.waitForTimeout(200);} }
  await p.click('[data-act=fight]'); await p.waitForTimeout(600); await p.screenshot({ path: 'r_btns.png' });
  await p.evaluate(()=>window.__T.setIdx(4)); await p.click('#runBtn'); await p.waitForTimeout(600);
  console.log('after run:', await p.evaluate(()=>window.__T.st())); await p.screenshot({ path: 'r_run.png' });
  for (const w of [250,1100]) { await p.setViewportSize({width:w,height:800}); await p.waitForTimeout(300);
    console.log(w, await p.evaluate(()=>[...document.querySelectorAll('.actions .btn')].map(b=>b.textContent.trim()+':'+(b.scrollWidth<=b.clientWidth+1?'ok':'CUT')).join(' | '))); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
