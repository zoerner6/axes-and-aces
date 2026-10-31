const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  const p = await b.newPage({ viewport: { width: 390, height: 820 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(500);
  await p.evaluate(()=>{ document.getElementById('overlay').hidden=true; window.__T.fin(); });
  for (const t of [800,1750,2600,2800,3600,4300]) { await p.waitForTimeout(t - (globalThis.last||0)); globalThis.last=t; await p.screenshot({ path: `f_${t}.png` }); }
  console.log(errs.join('|')||'no errors'); await b.close(); })();
