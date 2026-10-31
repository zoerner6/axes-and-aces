const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.addInitScript(()=>{ try{localStorage.setItem('aa_tutorialDone','true');localStorage.removeItem('aa_save')}catch(e){} });
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(400);
  for (const i of [0,1,2,4,5]) { console.log('after quest step', i, '->', await p.evaluate(i=>window.__T.go(i), i)); await p.waitForTimeout(200); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
