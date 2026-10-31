const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const errs=[];
  const p = await b.newPage({ viewport: { width: 390, height: 840 } }); p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(500);
  for (const [e,boss] of [['spot',0],['ambush',0],['path',0],['boss',1]]) { await p.evaluate(([e,boss])=>window.__T.enc(e,boss),[e,boss]); await p.waitForTimeout(3600); await p.screenshot({ path: `e_${e}.png` }); }
  await p.evaluate(()=>window.__T.enc('spot',0)); await p.waitForTimeout(1000); await p.screenshot({ path: 'e_spot_mid.png' });
  const q = await b.newPage({ viewport: { width: 1100, height: 820 } }); await q.goto('http://localhost:8765/test.html'); await q.waitForTimeout(500);
  await q.evaluate(()=>window.__T.enc('spot',0)); await q.waitForTimeout(3600); await q.screenshot({ path: 'e_desk.png' });
  console.log(errs.join('|')||'no errors'); await b.close(); })();
