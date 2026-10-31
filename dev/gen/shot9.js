const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const out=[];
  for (const [w,h] of [[250,700],[390,820],[1100,800]]) { const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('http://localhost:8765/test.html'); await p.waitForTimeout(600);
    await p.evaluate(()=>window.__T.boss()); await p.waitForTimeout(500); await p.click('[data-act=fight]'); await p.waitForTimeout(500); await p.click('.skip').catch(()=>{}); await p.waitForTimeout(600);
    await p.screenshot({ path: `v_${w}.png` });
    if(w===390){ await p.evaluate(()=>window.__T.trade()); await p.waitForTimeout(1500); await p.screenshot({ path: 'v_trade.png' }); }
  } await b.close(); })();
